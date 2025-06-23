import requests
from dotenv import load_dotenv
import os
import json
import csv
import flatdict
import pandas
# You must have a file called .env that has a line API_KEY=your-key
# replacing your-key with the api key that you get from the riot developer portal
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")



with open("People.json", "r") as f:
    SUMMONERS = json.load(f)





headers = {
    "X-Riot-Token": RIOT_API_KEY
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
    response = requests.get(url, headers=headers, params={"count" :10})

    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code, response.text)
        return None
    

def Match_data_from_match_id(match_id, player_puuid):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?{RIOT_API_KEY}"

    response = requests.get(url, headers=headers)
        #checks if the response is valid
    if response.status_code == 200:

        data = response.json()
        for player in data["info"]["participants"]:
            if player["puuid"] == player_puuid:
                    info_copy = data.get("info", {}).copy()
                    info_copy.pop("participants", None)
                    return {"player": player, "metadata": data.get("metadata", {}), "info" : info_copy}
    else:
        raise Exception(f"Failed to get Puuid: {response.status_code} - {response.text}")


def main():
    print(SUMMONERS["Trevor"]["puuid"])
    history = Get_Match_history(SUMMONERS["Trevor"]["puuid"])
    match_data = Match_data_from_match_id(history[7], SUMMONERS["Trevor"]["puuid"])
    
    print(match_data["metadata"])
    print(f" played {match_data['championName']} and had {match_data['kills']} kills and spent {match_data['totalTimeSpentDead']} seconds dead.")
    match_data = flatdict.FlatDict(match_data)
    match_data = pandas.DataFrame([match_data])
    match_data.to_csv('output.csv')



if __name__ == "__main__":
    print(Get_Puuid("americas", "mr patrick", "NA1"))
    print(Get_Puuid("americas", "jamminxdd", "NA1"))
    print(Get_Puuid("americas", "Snow Runt", "NA1"))
    print(Get_Puuid("americas", "Inkum", "NA1"))
    print(Get_Puuid("americas", "Cupcakefroster", "NA1"))
    print(Get_Puuid("americas", "Dorkus Aurelius", "NA1"))
    print(Get_Puuid("americas", "i love you", "gigaW"))
    print(Get_Puuid("americas", "ItsMeBBSUCC", "NA1"))
    #main()