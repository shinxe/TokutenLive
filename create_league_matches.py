import requests
from itertools import combinations

BASE_URL = "http://127.0.0.1:8000"
API_TOKEN = "secret-token"

def get_teams_for_league(sport, league):
    """Fetches all teams for a given league."""
    url = f"{BASE_URL}/leagues/{sport}/{league}/teams/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching teams: {e}")
        return []

def get_existing_matches(sport, league):
    """Fetches all existing matches for a given league."""
    url = f"{BASE_URL}/leagues/{sport}/{league}/matches/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching matches: {e}")
        return []

def create_match(payload):
    """Creates a new match."""
    url = f"{BASE_URL}/league_matches/"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Successfully created match: {payload['class1_id']} vs {payload['class2_id']}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating match for {payload['class1_id']} vs {payload['class2_id']}: {e}")
        if response is not None:
            print(f"Server response: {response.text}")

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
                # Sort by class_id to keep pairs consistent
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

def main():
    sport = "サッカー"
    league = "A"

    print(f"--- Generating matches for {sport} - {league} League ---")
    
    teams = get_teams_for_league(sport, league)
    if not teams:
        print("No teams found for this league. Exiting.")
        return

    existing_matches = get_existing_matches(sport, league)
    existing_pairs = set()
    for match in existing_matches:
        pair = tuple(sorted((match['class1']['id'], match['class2']['id'])))
        existing_pairs.add(pair)

    print(f"Found {len(teams)} teams and {len(existing_matches)} existing matches.")

    # Generate pairs using the new round-robin algorithm
    scheduled_pairs = generate_round_robin_pairs(list(teams)) # Pass a copy

    match_count = 0
    for team1_id, team2_id in scheduled_pairs:
        pair = (team1_id, team2_id)
        if pair not in existing_pairs:
            payload = {
                "sport": sport,
                "league": league,
                "class1_id": team1_id,
                "class2_id": team2_id,
                "class1_score": 0,
                "class2_score": 0,
                "class1_sets_won": 0,
                "class2_sets_won": 0,
                "winner_id": None
            }
            create_match(payload)
            match_count += 1
    
    if match_count == 0:
        print("No new matches needed. All pairs already exist.")
    else:
        print(f"--- Finished creating {match_count} new matches. ---")


if __name__ == "__main__":
    main()