import requests

API_KEY = "RGAPI-3b297c80-305b-4a07-8248-3900fa0ab50f"
SUMMONER_NAME = "King Kylan"
REGION = "na1"  # use appropriate routing value like euw1, kr, etc.
MATCH_REGION = "americas"  # for match-v5 (depends on summoner's region)

# Headers for Riot API
HEADERS = {
    "X-Riot-Token": API_KEY
}

def get_summoner_puuid(summoner_name):
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()['puuid']
    else:
        raise Exception(f"Failed to get PUUID: {response.status_code} - {response.text}")

def get_match_ids(puuid, count=10):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get match IDs: {response.status_code} - {response.text}")

def get_match_details(match_id):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get match details: {response.status_code} - {response.text}")

def main():
    try:
        puuid = get_summoner_puuid(SUMMONER_NAME)
        print(f"PUUID for {SUMMONER_NAME}: {puuid}")

        match_ids = get_match_ids(puuid)
        print(f"Recent Match IDs: {match_ids}")

        for match_id in match_ids:
            match_data = get_match_details(match_id)
            print(f"Match ID: {match_id}")
            print("Game Mode:", match_data['info']['gameMode'])
            print("Participants:", [p['summonerName'] for p in match_data['info']['participants']])
            print("-" * 40)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()