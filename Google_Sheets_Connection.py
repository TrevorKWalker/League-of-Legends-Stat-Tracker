import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth import default
from google.oauth2.credentials import Credentials
import os
import csv

# Define the scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def connect_to_client(token_path):
# Token file stores the user's access/refresh tokens
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

# If no valid creds, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

# Authorize gspread client
    client = gspread.authorize(creds)
    return client

# these next fours functions aren't neccassary as they are one line and therefore kinda redundant and useless
########################################
# Creates a spreadsheet with a given name
def create_spreadsheet(client, name):
    return client.create(name)
# Opens a spreadsheet with a given name
def open_spreadsheet(client, name):
    return client.open(name)  
# creates a worksheet
def create_worksheet(spreadsheet, name, rows = 100, cols = 100):
    return spreadsheet.add_worksheet(title=name, rows=rows, cols=cols)
# opens a worksheet
def open_worksheet(spreadsheet, name):
    return spreadsheet.worksheet(name)
######################################

#takes a worksheet and file path of a .csv file and clears the worksheet before upload the contents of the csv file
def upload_csv_to_worksheet(worksheet, csv_name):
    with open(csv_name, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    worksheet.update( data, "A1")
    print(f"CSV {csv_name} uploaded to {worksheet} in your Google Drive.")


if __name__ == "__main__":

    client = connect_to_client("trevor's_token.json")

    sh = open_spreadsheet(client, "new_spreadsheet test")
    ws = open_worksheet(sh, "Sheet1")
    upload_csv_to_worksheet(ws, "output.csv")