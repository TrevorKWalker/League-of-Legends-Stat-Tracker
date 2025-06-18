import requests
from dotenv import load_dotenv
import os


# You must have a file called .env that has a line API_KEY=your-key
# replacing your-key with the api key that you get from the riot developer portal
load_dotenv()
API_KEY = os.getenv("API_KEY")



SUMMONER_NAME = "King Kylan"
TAG_LINE = "NA1"
REGION = "americas"

#SUMMONER_NAME = "CalicoAze"
#TAG_LINE = "3023"
#REGION = "americas"

headers = {
    "X-Riot-Token": API_KEY
}

# Match_region needs to be the players region
# Summoner name is the username of the player in game
# tagline is is the #NA1 or tag that comes after the summoner name in client but without the #
def Get_Puuid(match_region, Summoner_name, tag_line):

    #get request that returns puuid 
    url = f"https://{match_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{Summoner_name}/{tag_line}"

    response = requests.get(url, headers=headers)
    
    #checks if the response is valid
    if response.status_code == 200:

        data = response.json()
        return data["puuid"]
    else:
        raise Exception(f"Failed to get Puuid: {response.status_code} - {response.text}")

def Get_Summoner(Puuid):

    #get request that returns puuid 
    url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{Puuid}"

    response = requests.get(url, headers=headers)
    
    #checks if the response is valid
    if response.status_code == 200:

        data = response.json()
        return data
    else:
        raise Exception(f"Failed to get Summoner: {response.status_code} - {response.text}")


def Get_Match_history(Puuid):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{Puuid}/ids"
    response = requests.get(url, headers=headers, params={"count" :50})

    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code, response.text)
        return None
    

def Match_data_from_match_id(match_id, player_puuid):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?{API_KEY}"
    response = requests.get(url, headers=headers)
        #checks if the response is valid
    if response.status_code == 200:

        data = response.json()
        for player in data["info"]["participants"]:
            if player["puuid"] == player_puuid:
                return player
    else:
        raise Exception(f"Failed to get Puuid: {response.status_code} - {response.text}")


def main():
    puuid = Get_Puuid(REGION,SUMMONER_NAME, TAG_LINE)
    print("Puuid is" , puuid)


    history = Get_Match_history(puuid)
    time = 0
    for match in history:

        recent_game = Match_data_from_match_id(history[0], puuid)
        time += recent_game['totalTimeSpentDead']
    print(time)
    print(f"{recent_game['riotIdGameName']} played {recent_game['championName']} and had {recent_game['kills']} kills and spent {recent_game['totalTimeSpentDead']} seconds dead.")




if __name__ == "__main__":
    main()