#local imports
import RiotApiConnection as RAC
import Google_Sheets_Connection as GSC

#libraries that are needed
import csv
import flatdict
import pandas
import json
import os
import dotenv

#API and ENV data
dotenv.load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
SUMMONERS = json.loads(os.getenv("Summoners"))




def match_data_to_csv(match_id, match_data, file ):
    if isinstance(match_id, list):
        match_data = pandas.DataFrame(match_data)
    else:
        match_data = pandas.DataFrame([match_data])
    match_data.insert(loc=0, column='MatchId', value=match_id)
    match_data.to_csv(file)


def batch_grab_match_data(match_ids, puuid):
    batch = []
    for match in match_ids:
        game_data = RAC.Match_data_from_match_id(match, puuid)
        batch.append(flatdict.FlatDict(game_data))
    return batch

def find_work_sheet(name, spreadsheet):
    worksheets = spreadsheet.worksheets()
    print(worksheets)
    for ws in worksheets:
        
        if  name == ws.title:
            return True
    return False


def create_new_player(Name, spreadsheet, file):
    #connection to Riot Api
    puuid = RAC.Get_Puuid(SUMMONERS[Name]["region"], SUMMONERS[Name]["Summoner_name"], SUMMONERS[Name]["tag"])
    match_ids = RAC.Get_Match_history(puuid)
    matches = batch_grab_match_data(match_ids, puuid)
    
    #write matches to csv
    match_data_to_csv(match_ids, matches, file)

    #write csv to google sheets
    client = GSC.connect_to_client("trevor's_token.json")
    sh = GSC.open_spreadsheet(client, spreadsheet)
    if find_work_sheet(Name, sh):
        ws = GSC.open_worksheet(sh, Name)
    else:
        ws = GSC.create_worksheet(sh, Name)
    ws.clear()
    GSC.upload_csv_to_worksheet(ws, file)



def update_player_sheet():
    
    history = RAC.Get_Match_history(SUMMONERS["Trevor"]["Puuid"])
    match_data = RAC.Match_data_from_match_id(history[7], SUMMONERS["Trevor"]["Puuid"])


def main():
    create_new_player("Trevor", "new_spreadsheet test", "output.csv")

if __name__ == "__main__":
    main()