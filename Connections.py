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
import gspread
import time
#API and ENV data
dotenv.load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
SUMMONERS = None

EXPECTED_COLUMNS = list(pandas.read_csv("columns.csv").columns)


def update_SUMMONERS():
    with open("People.json", "r") as f: 
        global SUMMONERS
        SUMMONERS = json.load(f)

def match_data_to_csv(match_id, match_data, file ):
    if isinstance(match_id, list):
        match_data = pandas.DataFrame(match_data)
    else:
        match_data = pandas.DataFrame([match_data])
    match_data.insert(loc=0, column='MatchId', value=match_id)

    match_data = match_data.reindex(columns=EXPECTED_COLUMNS)

    match_data.to_csv(file)


def batch_grab_match_data(match_ids, puuid):
    batch = []
    for match in match_ids:
        game_data = RAC.Match_data_from_match_id(match, puuid)
        batch.append(flatdict.FlatDict(game_data))
    return batch

def find_work_sheet(name, spreadsheet):
    worksheets = spreadsheet.worksheets()
    for ws in worksheets:
        
        if  name == ws.title:
            return True
    return False


def create_new_player(Name, spreadsheet, file):
    #connection to Riot Api
    puuid = RAC.Get_Puuid(SUMMONERS[Name]["region"], SUMMONERS[Name]["summoner_name"], SUMMONERS[Name]["tag"])
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



def update_player_sheet(name, spreadsheet, file):
    client = GSC.connect_to_client("trevor's_token.json")
    sh = GSC.open_spreadsheet(client, spreadsheet)

    if find_work_sheet(name, sh):
        ws = ws = GSC.open_worksheet(sh, name)
        last_match_id = ws.acell('B2').value
        match_ids = RAC.Get_Match_history(SUMMONERS[name]["puuid"])
        print(match_ids)

        for index, id in enumerate(match_ids):
            if id == last_match_id:
                print(index)
                match_ids = match_ids[0:index]
        print(match_ids)

        matches = batch_grab_match_data(match_ids,SUMMONERS[name]["puuid"] )
        match_data_to_csv(match_ids, matches, file)
        ws.insert_rows([['']] * len(match_ids), row = 2 )
        with open(file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        ws.update(rows, "A1")

    else:
        create_new_player(name, spreadsheet, file)

def main():
    #for person in SUMMONERS:
    #    update_player_sheet(person, "Discord bot stats", "output.csv")
    #    time.sleep(60)
    #create_new_player("Trevor", "new_spreadsheet test", "output.csv")
    pass


if __name__ == "__main__":
    update_SUMMONERS()
    #for person in SUMMONERS:
    #    print(person)

    main()