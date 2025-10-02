from sqlalchemy.orm import Session
from sqlalchemy import not_
from collections import defaultdict
import models, schemas
from fastapi import HTTPException

def calculate_league_standings(sport: models.SportName, league: models.LeagueName, db: Session):
    matches = db.query(models.LeagueMatch).filter(
        models.LeagueMatch.sport == sport,
        models.LeagueMatch.league == league
    ).all()

    stats = defaultdict(lambda: {"points": 0, "wins": 0, "losses": 0, "ties": 0, "sets_won": 0, "class_name": ""})
    
    all_class_ids = set()
    for match in matches:
        if not match.class1 or not match.class2:
            continue
        all_class_ids.add(match.class1_id)
        all_class_ids.add(match.class2_id)
        
        if not stats[match.class1_id]["class_name"]:
            stats[match.class1_id]["class_name"] = match.class1.name
        if not stats[match.class2_id]["class_name"]:
            stats[match.class2_id]["class_name"] = match.class2.name
            
        if match.is_finished:
            score1 = match.class1_score if match.class1_score is not None else 0
            score2 = match.class2_score if match.class2_score is not None else 0

            if score1 > score2:
                stats[match.class1_id]["points"] += 2
                stats[match.class1_id]["wins"] += 1
                stats[match.class2_id]["losses"] += 1
            elif score2 > score1:
                stats[match.class2_id]["points"] += 2
                stats[match.class2_id]["wins"] += 1
                stats[match.class1_id]["losses"] += 1
            else:
                stats[match.class1_id]["points"] += 1
                stats[match.class2_id]["points"] += 1
                stats[match.class1_id]["ties"] += 1
                stats[match.class2_id]["ties"] += 1

            if match.class1_sets_won is not None:
                stats[match.class1_id]["sets_won"] += match.class1_sets_won
            if match.class2_sets_won is not None:
                stats[match.class2_id]["sets_won"] += match.class2_sets_won

    sorted_class_ids = sorted(list(all_class_ids), key=lambda cid: (stats[cid]["points"], stats[cid]["sets_won"]), reverse=True)

    # Tie-breaking for teams with the same points
    for i in range(len(sorted_class_ids) - 1):
        for j in range(i + 1, len(sorted_class_ids)):
            id1 = sorted_class_ids[i]
            id2 = sorted_class_ids[j]

            if stats[id1]["points"] == stats[id2]["points"]:
                for m in matches:
                    if m.is_finished and {m.class1_id, m.class2_id} == {id1, id2}:
                        if m.winner_id == id2:
                            sorted_class_ids[i], sorted_class_ids[j] = sorted_class_ids[j], sorted_class_ids[i]
                        break

    league_points_map = {1: 12, 2: 10, 3: 8, 4: 6, 5: 4}
    standings = []
    for rank, class_id in enumerate(sorted_class_ids, 1):
        class_stats = stats[class_id]
        assigned_points = league_points_map.get(rank, 0)
            
        standings.append({
            "rank": rank,
            "class_id": class_id,
            "class_name": class_stats["class_name"],
            "points": class_stats["points"],
            "wins": class_stats["wins"],
            "losses": class_stats["losses"],
            "ties": class_stats["ties"],
            "sets_won_points": class_stats["sets_won"],
            "league_points": assigned_points
        })
        
    return standings



def generate_tournament_bracket(sport: models.SportName, db: Session):
    existing_matches = db.query(models.TournamentMatch).filter(models.TournamentMatch.sport == sport).first()
    if existing_matches:
        raise HTTPException(status_code=400, detail=f"{sport.value} tournament already generated.")

    standings = {}
    for league in models.LeagueName:
        standings[league.value] = calculate_league_standings(sport, league, db)
        if not standings[league.value]:
            raise HTTPException(status_code=404, detail=f"League {league.value} standings not available.")

    tournament_matches = []
    if sport in [models.SportName.SOCCER, models.SportName.VOLLEYBALL, models.SportName.MEN_BASKETBALL, models.SportName.WOMEN_BASKETBALL, models.SportName.SOFTBALL]:
        a1 = standings["A"][0]["class_id"]
        b1 = standings["B"][0]["class_id"]
        c1 = standings["C"][0]["class_id"]
        d1 = standings["D"][0]["class_id"]
        
        schedule = [
            {"name": "E1 (準決勝)", "c1": a1, "c2": b1},
            {"name": "E2 (準決勝)", "c1": c1, "c2": d1},
            {"name": "E3 (決勝)", "c1": None, "c2": None},
            {"name": "E4 (3位決定戦)", "c1": None, "c2": None},
        ]
    else:
        a1, a2 = standings["A"][0]["class_id"], standings["A"][1]["class_id"]
        b1, b2 = standings["B"][0]["class_id"], standings["B"][1]["class_id"]
        c1, c2 = standings["C"][0]["class_id"], standings["C"][1]["class_id"]
        d1, d2 = standings["D"][0]["class_id"], standings["D"][1]["class_id"]

        schedule = [
            {"name": "E1 (1回戦)", "c1": a1, "c2": b2},
            {"name": "E2 (1回戦)", "c1": c1, "c2": d2},
            {"name": "E3 (1回戦)", "c1": b1, "c2": c2},
            {"name": "E4 (1回戦)", "c1": d1, "c2": a2},
            {"name": "E5 (準決勝)", "c1": None, "c2": None},
            {"name": "E6 (準決勝)", "c1": None, "c2": None},
            {"name": "E7 (決勝)", "c1": None, "c2": None},
            {"name": "E8 (3位決定戦)", "c1": None, "c2": None},
        ]

    for match_info in schedule:
        db_match = models.TournamentMatch(
            sport=sport,
            match_name=match_info["name"],
            class1_id=match_info["c1"],
            class2_id=match_info["c2"]
        )
        db.add(db_match)
        tournament_matches.append(db_match)
    
    db.commit()
    for match in tournament_matches:
        db.refresh(match)
        
    return tournament_matches

def update_tournament_match(sport: models.SportName, match_id: int, match_data: schemas.TournamentMatchUpdate, db: Session):
    match_to_update = db.query(models.TournamentMatch).filter(
        models.TournamentMatch.id == match_id,
        models.TournamentMatch.sport == sport
    ).first()

    if not match_to_update:
        raise HTTPException(status_code=404, detail="Match not found.")

    # Update scores and winner
    match_to_update.class1_score = match_data.class1_score
    match_to_update.class2_score = match_data.class2_score
    match_to_update.class1_sets_won = match_data.class1_sets_won
    match_to_update.class2_sets_won = match_data.class2_sets_won
    match_to_update.winner_id = match_data.winner_id
    match_to_update.is_finished = True
    
    # Determine loser
    winner_id = match_data.winner_id
    if winner_id == match_to_update.class1_id:
        loser_id = match_to_update.class2_id
    elif winner_id == match_to_update.class2_id:
        loser_id = match_to_update.class1_id
    else:
        # This case might happen if participants are not yet decided for the match
        loser_id = None

    # Define advancement maps
    advancement_ball = {
        "E1 (準決勝)": {"winner_to": ("E3 (決勝)", "class1_id"), "loser_to": ("E4 (3位決定戦)", "class1_id")},
        "E2 (準決勝)": {"winner_to": ("E3 (決勝)", "class2_id"), "loser_to": ("E4 (3位決定戦)", "class2_id")},
    }
    advancement_racket = {
        "E1 (1回戦)": {"winner_to": ("E6 (準決勝)", "class1_id")},
        "E2 (1回戦)": {"winner_to": ("E6 (準決勝)", "class2_id")},
        "E3 (1回戦)": {"winner_to": ("E5 (準決勝)", "class1_id")},
        "E4 (1回戦)": {"winner_to": ("E5 (準決勝)", "class2_id")},
        "E5 (準決勝)": {"winner_to": ("E7 (決勝)", "class1_id"), "loser_to": ("E8 (3位決定戦)", "class1_id")},
        "E6 (準決勝)": {"winner_to": ("E7 (決勝)", "class2_id"), "loser_to": ("E8 (3位決定戦)", "class2_id")},
    }

    # Choose the correct map based on sport
    is_ball_game = sport in [models.SportName.SOCCER, models.SportName.VOLLEYBALL, models.SportName.MEN_BASKETBALL, models.SportName.WOMEN_BASKETBALL, models.SportName.SOFTBALL]
    advancement_map = advancement_ball if is_ball_game else advancement_racket

    # Process advancement if the match is in the map
    if match_to_update.match_name in advancement_map:
        rules = advancement_map[match_to_update.match_name]
        
        # Advance winner
        if "winner_to" in rules:
            next_match_name, position = rules["winner_to"]
            next_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name=next_match_name).first()
            if next_match:
                setattr(next_match, position, winner_id)

        # Advance loser (for semi-finals)
        if "loser_to" in rules and loser_id:
            next_match_name, position = rules["loser_to"]
            next_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name=next_match_name).first()
            if next_match:
                setattr(next_match, position, loser_id)

    db.commit()
    db.refresh(match_to_update)
    return match_to_update

def get_total_rankings(db: Session, skip: int = 0, limit: int = 100):
    all_classes = db.query(models.SchoolClass).all()
    class_points = defaultdict(lambda: {
        "total": 0,
        "league_details": defaultdict(int),
        "tournament_details": defaultdict(int)
    })

    # 1. Calculate League Points
    for sport in models.SportName:
        for league in models.LeagueName:
            matches = db.query(models.LeagueMatch).filter(
                models.LeagueMatch.sport == sport,
                models.LeagueMatch.league == league
            ).all()
            
            all_matches_finished = all(match.is_finished for match in matches) if matches else False

            if all_matches_finished:
                try:
                    standings = calculate_league_standings(sport, league, db)
                    for standing in standings:
                        class_id = standing["class_id"]
                        points = standing["league_points"]
                        class_points[class_id]["total"] += points
                        class_points[class_id]["league_details"][sport.value] += points
                except HTTPException as e:
                    if e.status_code == 404:
                        continue
                    raise e

    # 2. Calculate Tournament Points
    tournament_points_map = {"優勝": 10, "準優勝": 8, "3位": 6, "4位": 4}
    for sport in models.SportName:
        final_match = db.query(models.TournamentMatch).filter(
            models.TournamentMatch.sport == sport,
            models.TournamentMatch.match_name.contains("決勝"),
            not_(models.TournamentMatch.match_name.contains("準"))
        ).first()
        third_place_match = db.query(models.TournamentMatch).filter(models.TournamentMatch.sport == sport, models.TournamentMatch.match_name.contains("3位決定戦")).first()

        if final_match and final_match.is_finished and final_match.winner_id:
            winner_id = final_match.winner_id
            loser_id = None
            if final_match.class1_id and final_match.class2_id:
                loser_id = final_match.class2_id if winner_id == final_match.class1_id else final_match.class1_id

            if winner_id:
                class_points[winner_id]["total"] += tournament_points_map["優勝"]
                class_points[winner_id]["tournament_details"][sport.value] = tournament_points_map["優勝"]
            if loser_id:
                class_points[loser_id]["total"] += tournament_points_map["準優勝"]
                class_points[loser_id]["tournament_details"][sport.value] = tournament_points_map["準優勝"]

        if third_place_match and third_place_match.is_finished and third_place_match.winner_id:
            winner_id = third_place_match.winner_id
            loser_id = None
            if third_place_match.class1_id and third_place_match.class2_id:
                loser_id = third_place_match.class2_id if winner_id == third_place_match.class1_id else third_place_match.class1_id

            if winner_id:
                class_points[winner_id]["total"] += tournament_points_map["3位"]
                class_points[winner_id]["tournament_details"][sport.value] = tournament_points_map["3位"]
            if loser_id:
                class_points[loser_id]["total"] += tournament_points_map["4位"]
                class_points[loser_id]["tournament_details"][sport.value] = tournament_points_map["4位"]
            
    # 3. Format and Sort Rankings
    rankings_data = []
    for cls in all_classes:
        points_info = class_points[cls.id]
        rankings_data.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "total_points": points_info["total"],
            "league_points_details": dict(points_info["league_details"]),
            "tournament_points_details": dict(points_info["tournament_details"])
        })
        
    sorted_rankings = sorted(rankings_data, key=lambda x: x["total_points"], reverse=True)
    
    final_rankings = []
    for i, data in enumerate(sorted_rankings, 1):
        final_rankings.append({"rank": i, **data})
        
    return final_rankings[skip : skip + limit]

def generate_round_robin_pairs(teams):
    """Generates match pairs using the round-robin (circle) method, interleaved to maximize rest time."""
    if not teams:
        return []

    # If odd number of teams, add a dummy team for byes
    if len(teams) % 2:
        teams.append(None)
    
    n = len(teams)
    rounds = []
    for _ in range(n - 1):
        round_pairs = []
        for i in range(n // 2):
            team1 = teams[i]
            team2 = teams[n - 1 - i]
            if team1 and team2: # Ensure no Nones are paired
                pair = tuple(sorted((team1['id'], team2['id'])))
                round_pairs.append(pair)
        rounds.append(round_pairs) # Keep rounds separate
        
        # Rotate teams for next round, keeping first team fixed
        teams.insert(1, teams.pop())
        
    # Interleave the matches to spread them out
    interleaved_pairs = []
    if not rounds:
        return []
        
    num_matches_per_round = max(len(r) for r in rounds) if rounds else 0
    
    for i in range(num_matches_per_round):
        for j in range(len(rounds)):
            if i < len(rounds[j]):
                interleaved_pairs.append(rounds[j][i])
                
    return interleaved_pairs

def generate_league_matches(sport: models.SportName, league: models.LeagueName, db: Session):
    league_teams_query = db.query(models.LeagueTeam).filter_by(sport=sport, league=league).all()
    teams = [{'id': lt.class_id} for lt in league_teams_query]

    if len(teams) < 2:
        return {"message": "Not enough teams in the league to generate matches.", "created_count": 0}

    existing_matches_query = db.query(models.LeagueMatch).filter_by(sport=sport, league=league).all()
    existing_pairs = set()
    for match in existing_matches_query:
        pair = tuple(sorted((match.class1_id, match.class2_id)))
        existing_pairs.add(pair)

    scheduled_pairs = generate_round_robin_pairs(list(teams))

    created_count = 0
    for team1_id, team2_id in scheduled_pairs:
        pair = tuple(sorted((team1_id, team2_id)))
        if pair not in existing_pairs:
            new_match = models.LeagueMatch(
                sport=sport,
                league=league,
                class1_id=team1_id,
                class2_id=team2_id,
                is_finished=False
            )
            db.add(new_match)
            created_count += 1
    
    db.commit()
    
    return {"message": f"Successfully created {created_count} new matches.", "created_count": created_count}

def remove_team_from_league(team_data: schemas.LeagueTeamDelete, db: Session):
    team_to_delete = db.query(models.LeagueTeam).filter_by(
        sport=team_data.sport,
        league=team_data.league,
        class_id=team_data.class_id
    ).first()

    if not team_to_delete:
        raise HTTPException(status_code=404, detail="Team not found in this league")

    db.delete(team_to_delete)
    db.commit()
    return {"ok": True}

def delete_league_matches(sport: models.SportName, league: models.LeagueName, db: Session):
    """Deletes all matches and team associations for a given sport and league."""
    num_matches_deleted = db.query(models.LeagueMatch).filter(
        models.LeagueMatch.sport == sport,
        models.LeagueMatch.league == league
    ).delete(synchronize_session=False)

    num_teams_deleted = db.query(models.LeagueTeam).filter(
        models.LeagueTeam.sport == sport,
        models.LeagueTeam.league == league
    ).delete(synchronize_session=False)

    db.commit()
    return {"num_matches_deleted": num_matches_deleted, "num_teams_deleted": num_teams_deleted}

def delete_all_league_data(db: Session):
    """Deletes all league matches, tournament matches, and team associations from the database."""
    num_matches_deleted = db.query(models.LeagueMatch).delete(synchronize_session=False)
    num_teams_deleted = db.query(models.LeagueTeam).delete(synchronize_session=False)
    num_tournament_matches_deleted = db.query(models.TournamentMatch).delete(synchronize_session=False)
    db.commit()
    return {
        "num_matches_deleted": num_matches_deleted,
        "num_teams_deleted": num_teams_deleted,
        "num_tournament_matches_deleted": num_tournament_matches_deleted,
    }

def delete_all_scores(db: Session):
    """Deletes all league and tournament matches, but keeps team associations."""
    num_league_matches_deleted = db.query(models.LeagueMatch).delete(synchronize_session=False)
    num_tournament_matches_deleted = db.query(models.TournamentMatch).delete(synchronize_session=False)
    db.commit()
    return {
        "num_league_matches_deleted": num_league_matches_deleted,
        "num_tournament_matches_deleted": num_tournament_matches_deleted,
    }
    match_to_update = db.query(models.TournamentMatch).filter(
        models.TournamentMatch.id == match_id,
        models.TournamentMatch.sport == sport
    ).first()

    if not match_to_update:
        raise HTTPException(status_code=404, detail="Match not found.")

    # Update scores and winner
    match_to_update.class1_score = match_data.class1_score
    match_to_update.class2_score = match_data.class2_score
    match_to_update.class1_sets_won = match_data.class1_sets_won
    match_to_update.class2_sets_won = match_data.class2_sets_won
    match_to_update.winner_id = match_data.winner_id
    match_to_update.is_finished = True
    
    # Determine loser
    winner_id = match_data.winner_id
    if winner_id == match_to_update.class1_id:
        loser_id = match_to_update.class2_id
    elif winner_id == match_to_update.class2_id:
        loser_id = match_to_update.class1_id
    else:
        # This case might happen if participants are not yet decided for the match
        loser_id = None

    # Define advancement maps
    advancement_ball = {
        "E1 (準決勝)": {"winner_to": ("E3 (決勝)", "class1_id"), "loser_to": ("E4 (3位決定戦)", "class1_id")},
        "E2 (準決勝)": {"winner_to": ("E3 (決勝)", "class2_id"), "loser_to": ("E4 (3位決定戦)", "class2_id")},
    }
    advancement_racket = {
        "E1 (1回戦)": {"winner_to": ("E6 (準決勝)", "class1_id")},
        "E2 (1回戦)": {"winner_to": ("E6 (準決勝)", "class2_id")},
        "E3 (1回戦)": {"winner_to": ("E5 (準決勝)", "class1_id")},
        "E4 (1回戦)": {"winner_to": ("E5 (準決勝)", "class2_id")},
        "E5 (準決勝)": {"winner_to": ("E7 (決勝)", "class1_id"), "loser_to": ("E8 (3位決定戦)", "class1_id")},
        "E6 (準決勝)": {"winner_to": ("E7 (決勝)", "class2_id"), "loser_to": ("E8 (3位決定戦)", "class2_id")},
    }

    # Choose the correct map based on sport
    is_ball_game = sport in [models.SportName.SOCCER, models.SportName.VOLLEYBALL, models.SportName.MEN_BASKETBALL, models.SportName.WOMEN_BASKETBALL, models.SportName.SOFTBALL]
    advancement_map = advancement_ball if is_ball_game else advancement_racket

    # Process advancement if the match is in the map
    if match_to_update.match_name in advancement_map:
        rules = advancement_map[match_to_update.match_name]
        
        # Advance winner
        if "winner_to" in rules:
            next_match_name, position = rules["winner_to"]
            next_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name=next_match_name).first()
            if next_match:
                setattr(next_match, position, winner_id)

        # Advance loser (for semi-finals)
        if "loser_to" in rules and loser_id:
            next_match_name, position = rules["loser_to"]
            next_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name=next_match_name).first()
            if next_match:
                setattr(next_match, position, loser_id)

    db.commit()
    db.refresh(match_to_update)
    return match_to_update

def get_total_rankings(db: Session, skip: int = 0, limit: int = 100):
    all_classes = db.query(models.SchoolClass).all()
    class_points = defaultdict(lambda: {
        "total": 0,
        "league_details": defaultdict(int),
        "tournament_details": defaultdict(int)
    })

    # 1. Calculate League Points
    for sport in models.SportName:
        for league in models.LeagueName:
            matches = db.query(models.LeagueMatch).filter(
                models.LeagueMatch.sport == sport,
                models.LeagueMatch.league == league
            ).all()
            
            all_matches_finished = all(match.is_finished for match in matches) if matches else False

            if all_matches_finished:
                try:
                    standings = calculate_league_standings(sport, league, db)
                    for standing in standings:
                        class_id = standing["class_id"]
                        points = standing["league_points"]
                        class_points[class_id]["total"] += points
                        class_points[class_id]["league_details"][sport.value] += points
                except HTTPException as e:
                    if e.status_code == 404:
                        continue
                    raise e

    # 2. Calculate Tournament Points
    tournament_points_map = {"優勝": 10, "準優勝": 8, "3位": 6, "4位": 4}
    for sport in models.SportName:
        final_match = db.query(models.TournamentMatch).filter(
            models.TournamentMatch.sport == sport,
            models.TournamentMatch.match_name.contains("決勝"),
            not_(models.TournamentMatch.match_name.contains("準"))
        ).first()
        third_place_match = db.query(models.TournamentMatch).filter(models.TournamentMatch.sport == sport, models.TournamentMatch.match_name.contains("3位決定戦")).first()

        if final_match and final_match.is_finished and final_match.winner_id:
            winner_id = final_match.winner_id
            loser_id = None
            if final_match.class1_id and final_match.class2_id:
                loser_id = final_match.class2_id if winner_id == final_match.class1_id else final_match.class1_id

            if winner_id:
                class_points[winner_id]["total"] += tournament_points_map["優勝"]
                class_points[winner_id]["tournament_details"][sport.value] = tournament_points_map["優勝"]
            if loser_id:
                class_points[loser_id]["total"] += tournament_points_map["準優勝"]
                class_points[loser_id]["tournament_details"][sport.value] = tournament_points_map["準優勝"]

        if third_place_match and third_place_match.is_finished and third_place_match.winner_id:
            winner_id = third_place_match.winner_id
            loser_id = None
            if third_place_match.class1_id and third_place_match.class2_id:
                loser_id = third_place_match.class2_id if winner_id == third_place_match.class1_id else third_place_match.class1_id

            if winner_id:
                class_points[winner_id]["total"] += tournament_points_map["3位"]
                class_points[winner_id]["tournament_details"][sport.value] = tournament_points_map["3位"]
            if loser_id:
                class_points[loser_id]["total"] += tournament_points_map["4位"]
                class_points[loser_id]["tournament_details"][sport.value] = tournament_points_map["4位"]
            
    # 3. Format and Sort Rankings
    rankings_data = []
    for cls in all_classes:
        points_info = class_points[cls.id]
        rankings_data.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "total_points": points_info["total"],
            "league_points_details": dict(points_info["league_details"]),
            "tournament_points_details": dict(points_info["tournament_details"])
        })
        
    sorted_rankings = sorted(rankings_data, key=lambda x: x["total_points"], reverse=True)
    
    final_rankings = []
    for i, data in enumerate(sorted_rankings, 1):
        final_rankings.append({"rank": i, **data})
        
    return final_rankings[skip : skip + limit]

def generate_round_robin_pairs(teams):
    """Generates match pairs using the round-robin (circle) method, interleaved to maximize rest time."""
    if not teams:
        return []

    # If odd number of teams, add a dummy team for byes
    if len(teams) % 2:
        teams.append(None)
    
    n = len(teams)
    rounds = []
    for _ in range(n - 1):
        round_pairs = []
        for i in range(n // 2):
            team1 = teams[i]
            team2 = teams[n - 1 - i]
            if team1 and team2: # Ensure no Nones are paired
                pair = tuple(sorted((team1['id'], team2['id'])))
                round_pairs.append(pair)
        rounds.append(round_pairs) # Keep rounds separate
        
        # Rotate teams for next round, keeping first team fixed
        teams.insert(1, teams.pop())
        
    # Interleave the matches to spread them out
    interleaved_pairs = []
    if not rounds:
        return []
        
    num_matches_per_round = max(len(r) for r in rounds) if rounds else 0
    
    for i in range(num_matches_per_round):
        for j in range(len(rounds)):
            if i < len(rounds[j]):
                interleaved_pairs.append(rounds[j][i])
                
    return interleaved_pairs

def generate_league_matches(sport: models.SportName, league: models.LeagueName, db: Session):
    league_teams_query = db.query(models.LeagueTeam).filter_by(sport=sport, league=league).all()
    teams = [{'id': lt.class_id} for lt in league_teams_query]

    if len(teams) < 2:
        return {"message": "Not enough teams in the league to generate matches.", "created_count": 0}

    existing_matches_query = db.query(models.LeagueMatch).filter_by(sport=sport, league=league).all()
    existing_pairs = set()
    for match in existing_matches_query:
        pair = tuple(sorted((match.class1_id, match.class2_id)))
        existing_pairs.add(pair)

    scheduled_pairs = generate_round_robin_pairs(list(teams))

    created_count = 0
    for team1_id, team2_id in scheduled_pairs:
        pair = tuple(sorted((team1_id, team2_id)))
        if pair not in existing_pairs:
            new_match = models.LeagueMatch(
                sport=sport,
                league=league,
                class1_id=team1_id,
                class2_id=team2_id,
                is_finished=False
            )
            db.add(new_match)
            created_count += 1
    
    db.commit()
    
    return {"message": f"Successfully created {created_count} new matches.", "created_count": created_count}

def remove_team_from_league(team_data: schemas.LeagueTeamDelete, db: Session):
    team_to_delete = db.query(models.LeagueTeam).filter_by(
        sport=team_data.sport,
        league=team_data.league,
        class_id=team_data.class_id
    ).first()

    if not team_to_delete:
        raise HTTPException(status_code=404, detail="Team not found in this league")

    db.delete(team_to_delete)
    db.commit()
    return {"ok": True}

def delete_league_matches(sport: models.SportName, league: models.LeagueName, db: Session):
    """Deletes all matches and team associations for a given sport and league."""
    num_matches_deleted = db.query(models.LeagueMatch).filter(
        models.LeagueMatch.sport == sport,
        models.LeagueMatch.league == league
    ).delete(synchronize_session=False)

    num_teams_deleted = db.query(models.LeagueTeam).filter(
        models.LeagueTeam.sport == sport,
        models.LeagueTeam.league == league
    ).delete(synchronize_session=False)

    db.commit()
    return {"num_matches_deleted": num_matches_deleted, "num_teams_deleted": num_teams_deleted}

def delete_all_league_data(db: Session):
    """Deletes all league matches, tournament matches, and team associations from the database."""
    num_matches_deleted = db.query(models.LeagueMatch).delete(synchronize_session=False)
    num_teams_deleted = db.query(models.LeagueTeam).delete(synchronize_session=False)
    num_tournament_matches_deleted = db.query(models.TournamentMatch).delete(synchronize_session=False)
    db.commit()
    return {
        "num_matches_deleted": num_matches_deleted,
        "num_teams_deleted": num_teams_deleted,
        "num_tournament_matches_deleted": num_tournament_matches_deleted,
    }