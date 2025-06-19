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

def Create_and_Write_To_Spreadsheet(file, name, token_path):
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

# Create new spreadsheet in your Google Drive
    spreadsheet = client.create(name)

# Open the first sheet
    sheet = spreadsheet.sheet1

# Read and parse CSV
    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

# Insert data starting at A1
    sheet.update("A1", data)

    print("Spreadsheet created and CSV uploaded in your Google Drive.")


if __name__ == "__main__":
    Create_and_Write_To_Spreadsheet("tester.csv", "new_spreadsheet test" , "trevor's_token.json")