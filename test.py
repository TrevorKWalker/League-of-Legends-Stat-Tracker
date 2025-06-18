import requests

API_KEY = "RGAPI-0d0981e5-b09b-406d-aaaa-fa2e318d13fe"
SUMMONER_NAME = "King Kylan"
TAG_LINE = "NA1"
REGION = "americas"

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
    url = f"https://api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{Puuid}"

    response = requests.get(url, headers=headers)
    
    #checks if the response is valid
    if response.status_code == 200:

        data = response.json()
        return data["puuid"]
    else:
        raise Exception(f"Failed to get Puuid: {response.status_code} - {response.text}")
def main():
    puuid = Get_Puuid(REGION,SUMMONER_NAME, TAG_LINE)
    print("Puuid is" , puuid)


if __name__ == "__main__":
    main()