from sqlalchemy.orm import Session
from collections import defaultdict
import models
from fastapi import HTTPException

def calculate_league_standings(sport: models.SportName, league: models.LeagueName, db: Session):
    matches = db.query(models.LeagueMatch).filter(
        models.LeagueMatch.sport == sport,
        models.LeagueMatch.league == league
    ).all()

    stats = defaultdict(lambda: {"wins": 0, "losses": 0, "sets_won": 0, "class_name": ""})
    
    all_class_ids = set()
    for match in matches:
        all_class_ids.add(match.class1_id)
        all_class_ids.add(match.class2_id)
        
        # Populate class names
        if not stats[match.class1_id]["class_name"]:
            stats[match.class1_id]["class_name"] = match.class1.name
        if not stats[match.class2_id]["class_name"]:
            stats[match.class2_id]["class_name"] = match.class2.name
            
        # Update stats based on winner
        winner_id = match.winner_id
        loser_id = match.class2_id if winner_id == match.class1_id else match.class1_id
        
        stats[winner_id]["wins"] += 1
        stats[loser_id]["losses"] += 1
        
        stats[match.class1_id]["sets_won"] += match.class1_sets_won
        stats[match.class2_id]["sets_won"] += match.class2_sets_won
        
    # --- Sorting Logic ---
    # Primary sort key
    if sport in [models.SportName.TABLE_TENNIS, models.SportName.BADMINTON]:
        sort_key = lambda class_id: stats[class_id]["sets_won"]
    else:
        sort_key = lambda class_id: stats[class_id]["wins"]
        
    sorted_class_ids = sorted(list(all_class_ids), key=sort_key, reverse=True)
    
    # Tie-breaker logic
    for i in range(len(sorted_class_ids) - 1):
        for j in range(i + 1, len(sorted_class_ids)):
            id1 = sorted_class_ids[i]
            id2 = sorted_class_ids[j]

            # If scores are tied, check head-to-head
            if sort_key(id1) == sort_key(id2):
                for match in matches:
                    if {match.class1_id, match.class2_id} == {id1, id2}:
                        if match.winner_id == id2:
                            # Swap if id2 won against id1
                            sorted_class_ids[i], sorted_class_ids[j] = sorted_class_ids[j], sorted_class_ids[i]
                        break

    # --- Point Assignment ---
    league_points_map = {1: 12, 2: 10, 3: 8, 4: 6, 5: 4}
    standings = []
    for rank, class_id in enumerate(sorted_class_ids, 1):
        class_stats = stats[class_id]
        
        assigned_points = 0
        if sport not in [models.SportName.TABLE_TENNIS, models.SportName.BADMINTON]:
            assigned_points = league_points_map.get(rank, 0)
            
        standings.append({
            "rank": rank,
            "class_id": class_id,
            "class_name": class_stats["class_name"],
            "wins": class_stats["wins"],
            "losses": class_stats["losses"],
            "sets_won_points": class_stats["sets_won"],
            "league_points": assigned_points
        })
        
    return standings

#決勝


def generate_tournament_bracket(sport: models.SportName, db: Session):
    # Check if tournament already exists
    existing_matches = db.query(models.TournamentMatch).filter(models.TournamentMatch.sport == sport).first()
    if existing_matches:
        raise HTTPException(status_code=400, detail=f"{sport.value} tournament already generated.")

    # Get league standings
    standings = {}
    for league in models.LeagueName:
        standings[league.value] = calculate_league_standings(sport, league, db)
        if not standings[league.value]:
            raise HTTPException(status_code=404, detail=f"League {league.value} standings not available.")

    tournament_matches = []
    if sport in [models.SportName.SOCCER, models.SportName.VOLLEYBALL, models.SportName.BASKETBALL]:
        # 4-team tournament
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
        # 8-team tournament
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

def update_tournament_match(sport: models.SportName, match_id: int, winner_id: int, db: Session):
    match_to_update = db.query(models.TournamentMatch).filter(
        models.TournamentMatch.id == match_id,
        models.TournamentMatch.sport == sport
    ).first()

    if not match_to_update:
        raise HTTPException(status_code=404, detail="Match not found.")
    
    match_to_update.winner_id = winner_id
    
    # --- Logic for advancing the winner ---
    
    # For 4-team tournaments
    if sport in [models.SportName.SOCCER, models.SportName.VOLLEYBALL, models.SportName.BASKETBALL]:
        if match_to_update.match_name == "E1 (準決勝)":
            next_match_final = db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E3 (決勝)").first()
            next_match_final.class1_id = winner_id
        elif match_to_update.match_name == "E2 (準決勝)":
            next_match_final = db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E3 (決勝)").first()
            next_match_final.class2_id = winner_id
        
        # Logic for 3rd place match
        loser_id = match_to_update.class1_id if winner_id == match_to_update.class2_id else match_to_update.class2_id
        if match_to_update.match_name == "E1 (準決勝)":
            third_place_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E4 (3位決定戦)").first()
            third_place_match.class1_id = loser_id
        elif match_to_update.match_name == "E2 (準決勝)":
            third_place_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E4 (3位決定戦)").first()
            third_place_match.class2_id = loser_id
            
    # For 8-team tournaments
    else:
        advancement_map = {
            "E1 (1回戦)": ("E6 (準決勝)", "class1_id"),
            "E2 (1回戦)": ("E6 (準決勝)", "class2_id"),
            "E3 (1回戦)": ("E5 (準決勝)", "class1_id"),
            "E4 (1回戦)": ("E5 (準決勝)", "class2_id"),
            "E5 (準決勝)": ("E7 (決勝)", "class1_id"),
            "E6 (準決勝)": ("E7 (決勝)", "class2_id"),
        }
        
        if match_to_update.match_name in advancement_map:
            next_match_name, position = advancement_map[match_to_update.match_name]
            next_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name=next_match_name).first()
            setattr(next_match, position, winner_id)

        # Logic for 3rd place match
        if "準決勝" in match_to_update.match_name:
            loser_id = match_to_update.class1_id if winner_id == match_to_update.class2_id else match_to_update.class2_id
            third_place_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E8 (3位決定戦)").first()
            if match_to_update.match_name == "E5 (準決勝)":
                third_place_match.class1_id = loser_id
            elif match_to_update.match_name == "E6 (準決勝)":
                third_place_match.class2_id = loser_id

    db.commit()
    db.refresh(match_to_update)
    return match_to_update



def get_total_rankings(db: Session):
    all_classes = db.query(models.SchoolClass).all()
    class_points = defaultdict(lambda: {
        "total": 0,
        "league_details": defaultdict(int),
        "tournament_details": defaultdict(int)
    })

    # 1. Calculate League Points
    for sport in models.SportName:
        for league in models.LeagueName:
            try:
                standings = calculate_league_standings(sport, league, db)
                for standing in standings:
                    class_id = standing["class_id"]
                    points = standing["league_points"] if sport not in [models.SportName.TABLE_TENNIS, models.SportName.BADMINTON] else standing["sets_won_points"]
                    class_points[class_id]["total"] += points
                    class_points[class_id]["league_details"][sport.value] += points
            except HTTPException as e:
                # This league might not have matches, so we can ignore it.
                if e.status_code == 404:
                    continue
                raise e

    # 2. Calculate Tournament Points
    tournament_points_map = {"優勝": 10, "準優勝": 8, "3位": 6, "4位": 4}
    for sport in models.SportName:
        final_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E7 (決勝)").first() or \
                      db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E3 (決勝)").first()
        third_place_match = db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E8 (3位決定戦)").first() or \
                            db.query(models.TournamentMatch).filter_by(sport=sport, match_name="E4 (3位決定戦)").first()

        if final_match and final_match.winner_id:
            winner_id = final_match.winner_id
            loser_id = final_match.class1_id if winner_id == final_match.class2_id else final_match.class2_id
            
            # 1st Place
            class_points[winner_id]["total"] += tournament_points_map["優勝"]
            class_points[winner_id]["tournament_details"][sport.value] = tournament_points_map["優勝"]
            # 2nd Place
            class_points[loser_id]["total"] += tournament_points_map["準優勝"]
            class_points[loser_id]["tournament_details"][sport.value] = tournament_points_map["準優勝"]

        if third_place_match and third_place_match.winner_id:
            winner_id = third_place_match.winner_id
            loser_id = third_place_match.class1_id if winner_id == third_place_match.class2_id else third_place_match.class2_id
            
            # 3rd Place
            class_points[winner_id]["total"] += tournament_points_map["3位"]
            class_points[winner_id]["tournament_details"][sport.value] = tournament_points_map["3位"]
            # 4th Place
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
        
    return final_rankings