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


#list of the normalized columns so that all entries contain the same number of  columns and in the right order
# This is needed because some games the api wont gather data on certain events if they aren't applicable like baron gold advantage
EXPECTED_COLUMNS = list(pandas.read_csv("columns.csv").columns)

##### function called by discord_bot.py to update the SUMMONERS object when a new member is added.
def update_SUMMONERS():
    #opens the appropriate file and loads the data object into a global SUMMONERS variable
    with open("People.json", "r") as f: 
        global SUMMONERS
        SUMMONERS = json.load(f)

##### function to upload the match data to a file for easy of upload to the Google Sheet
# takes the match id which can be a single id or a list, match data which can also be single match or list but must be equal length to the ids and a file 
# they should always be same length as the ids are used to get the data and immediately passed to this function.
# file is almost always "output.csv"
def match_data_to_csv(match_id, match_data, file ):
    #checks if it is a single match or a list of matches
    if isinstance(match_id, list):
        #if it is a list then we use this 
        match_data = pandas.DataFrame(match_data)
    else:
        # if it is a single match we need to make it a list then convert
        match_data = pandas.DataFrame([match_data])
    #then we insert the match ids in the first column so that it is easy to find later when updating
    match_data.insert(loc=0, column='MatchId', value=match_id)
    # we normalize to ensure that every column that we expect to see is accounted for and if it isnt then a NaN is inserted to that entry to ensure alignment in the google sheet
    match_data = match_data.reindex(columns=EXPECTED_COLUMNS)
    #and then we write it to the file which is probably "output.csv"
    match_data.to_csv(file)

##### Function that grabs the match data from a players puuid and a list of match ids
# match ids must be a list
def batch_grab_match_data(match_ids : list, puuid):
    batch = []
    #iterates through the ids and makes a call to get the data for each one
    for match in match_ids:
        game_data = RAC.Match_data_from_match_id(match, puuid)
        #then appends it to batch after flattening it to make it easier to proccess
        batch.append(flatdict.FlatDict(game_data))
    return batch

##### simple function to find if a worksheet exist within a spreadsheet 
def find_work_sheet(name, spreadsheet):
    worksheets = spreadsheet.worksheets()
    #iterates through every worksheet and checks the name
    for ws in worksheets:
        #if we find a worksheet with the matching name then we return True
        if  name == ws.title:
            return True
    #if we exhausts all worksheets without a match we return false
    return False

# function to add a new player to the google sheet 
# takes a name and the spreadsheet, name will become the name of the worksheet 
# Name must be a key in the SUMMONERS data object with all relevent fields filled out.
def create_new_player(Name, spreadsheet):
    #### connection to Riot Api using name as the key
    puuid = RAC.Get_Puuid(SUMMONERS[Name]["region"], SUMMONERS[Name]["summoner_name"], SUMMONERS[Name]["tag"])
    match_ids = RAC.Get_Match_history(puuid)
    matches = batch_grab_match_data(match_ids, puuid)
    
    #write matches to csv and ensures that all columns are normalized 
    # which makes it so that it will always line up with the other entries.
    match_data_to_csv(match_ids, matches, "output.csv")

    #### write csv to google sheets
    #connects to the spreadsheet using my api key and opens it 
    client = GSC.connect_to_client("trevor's_token.json")
    sh = GSC.open_spreadsheet(client, spreadsheet)
    #if the worksheet exist it opens it
    if find_work_sheet(Name, sh):
        ws = GSC.open_worksheet(sh, Name)
    #if it doesnt exist then we create a worksheet. This is the expected path for a new user
    else:
        ws = GSC.create_worksheet(sh, Name)
    # we clear the ws because this is a new user so if there was a worksheet and we opened it 
    # it might have unwanted data. There is protection against doing this to an existing user in Discord_bot.py new_user function 
    # which should be the only funtion that calls this one.
    ws.clear()
    #then we upload all the matches to the worksheet.
    GSC.upload_csv_to_worksheet(ws, "output.csv")


##### Function to update a players sheet with their most recent games. 
# takes a name and spreadsheet where name is a key in the SUMMONERS data object and the name of a worksheet in the spreadsheet
def update_player_sheet(name, spreadsheet):
    # establish a connection to the google drive account and then to the spreadsheet to allow for error checking
    client = GSC.connect_to_client("trevor's_token.json")
    sh = GSC.open_spreadsheet(client, spreadsheet)
    # error checking for finding the worksheet
    if find_work_sheet(name, sh):
        #if the worksheet is found properly then we open it and grab the most recent match id.
        # that value will always be stored in B2 for a valid worksheet with priopr entries.
        # no sheet should be empty due to the creation function adding the 20 most recent games but if it is
        # then the value will be none which works with the rest of the program
        ws = GSC.open_worksheet(sh, name)
        last_match_id = ws.acell('B2').value
        #then we grab 20 match ids 
        match_ids = RAC.Get_Match_history(SUMMONERS[name]["puuid"])
        #and check to see if any of them match the most recent one 
        # We expect this to find the most recent one at some point in those 20 games.
        # the code should run once a day so as long as the user doesnt play more than 20 games in one day it will work as expected
        # any more than 20 games and the bot will only pull the most recent 20 to add
        for index, id in enumerate(match_ids):
            if id == last_match_id:
                match_ids = match_ids[0:index]
        #once we have the list of ids we care about we grab the data 
        matches = batch_grab_match_data(match_ids,SUMMONERS[name]["puuid"] )
        match_data_to_csv(match_ids, matches, "output.csv")
        # this inserts rows on the worksheet equal to the number of new games so that we can insert the games to the top of the worksheet.
        ws.insert_rows([['']] * len(match_ids), row = 2 )
        #finally we write the games to the worksheet
        with open("output.csv", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        ws.update(rows, "A1")

    else:
        #if we cant find the worksheet we treat it as a new player
        #this shouldn't ever happen due to the error checking in discord_bot.py
        create_new_player(name, spreadsheet)




##### function to create a scoreboard
# will do two things: update the scoreboard page of the google sheets and create a Current_scoreboard.json with all the data
# stat needs to be a valid key found in scoreboards.json same with qualifier
def create_scoreboard(spreadsheet, stat, qualifier):
    #open scoreboards.json which holds all valid scoreboards
    with open("scoreboards.json", "r") as f:
        scoreboards = json.load(f)
    #error is raised if our key doesnt match
    if stat not in scoreboards:
        raise KeyError
    #error is raised if our key doesnt match
    if qualifier not in scoreboards[stat]:
        raise KeyError
    # establish a connection to the google drive account and then to the spreadsheet to allow for error checking
    client = GSC.connect_to_client("trevor's_token.json")
    sh = GSC.open_spreadsheet(client, spreadsheet)

    #create our dicitonary for holding all the data we need
    new_board = {}
    #start time allows us to check against games and check how long the scoreboard has been running for
    start_time = time.time()

    #these statments initialize the board with all the information that is found in scoreboards.json
    new_board = scoreboards[stat][qualifier]

    new_board["start_time"] = start_time * 1000
    new_board["participants"] = {}
    #get all worksheets
    worksheets = sh.worksheets()
    #iterates through every worksheet and checks the name
    """for ws in worksheets:
        # as long as the names arent one of the two non player sheets we add the player and initialize to none
        if ws.title != "HOME" and ws.title != "Scoreboard":
            if new_board["function"] == "max":
                new_board["participants"][ws.title] = 0"""
            
    # write our board to the current_board.json file to save it
    with open("Curent_scorboard.json", "w") as f:
        json.dump(new_board, f, indent = 2)
    
    #This part is to update the google spreadsheet and more specically the Scoreboard worksheet
    scoreboard_ws = GSC.open_worksheet(sh,"Scoreboard")
    scoreboard_ws.update("A1", [[new_board["title"]]])
    scoreboard_ws.update("A5", [[new_board["description"]]])
    scoreboard_ws.update("A8", [["Participants"]])
    scoreboard_ws.update("C8", [[new_board["stat"]]])
    index = 9
    for participant in new_board["participants"]:
        scoreboard_ws.update(f"A{index}",[[participant]])
        scoreboard_ws.update(f"C{index}", [[new_board["participants"][participant]]])
        index += 1




def update_scoreboard():
    with open("Curent_scorboard.json", "r") as f:
        board = json.load(f)
    client = GSC.connect_to_client("trevor's_token.json")
    sh = GSC.open_spreadsheet(client, "Discord bot stats")
    scoreboard_ws = GSC.open_worksheet(sh,"Scoreboard")
    for player in SUMMONERS:
        ws = GSC.open_worksheet(sh, player)
        
        times = ws.col_values(4)[1:]
        for index, time in enumerate(times):
            if float(time) < board["start_time"]:
                times = times[:index]
                continue
        if(len(times) != 0):
            stat = None
            if board["function"] == "max":
                stat = max([int(x) for x in ws.col_values(board["column"])[1:len(times)+1]])
            elif board["function"] == "min":
                stat = max([int(x) for x in ws.col_values(board["column"])[1:len(times)+1]])
                
            if stat is not None:
                if player not in board["participants"]:
                    board["participants"][player] = stat
                elif stat > board["participants"][player]:
                    board["participants"][player] = stat
    with open("Curent_scorboard.json", "w") as f:
        json.dump(board, f, indent = 2)
    data =[]
    for key, value in board["participants"].items():
        data.append([key, "", value])
    scoreboard_ws.update(data,"A9")
    
    data = scoreboard_ws.get_all_values()
    rows = data[8:]
    rows.sort(key=lambda x: int(x[2]), reverse= board["sort_reverse"])

    result = {row[0]: row[2] for row in data if len(row) >= 3 and row[0]}
    board
    scoreboard_ws.update("A9", rows)







###########
# Testing #
###########
#everything below this is for testing only and is never and should never be called by the bot
def main():

    for person in SUMMONERS:
        update_player_sheet(person, "Discord bot stats")
        time.sleep(60)
    #create_new_player("Trevor", "new_spreadsheet test", "output.csv")
    pass


if __name__ == "__main__":
    pass
    #update_SUMMONERS()
    #main()