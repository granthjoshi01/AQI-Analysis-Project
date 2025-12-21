import gspread
from google.oauth2.service_account import Credentials

# Scope: allow read/write to Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Path to your service account key
SERVICE_ACCOUNT_FILE = "your_json_file"

# Google Sheet details
SPREADSHEET_NAME = "NAME_OF_SPREADSHEET"
WORKSHEET_NAME = "NAME_OF_WORKSHEET"

def main():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    # Write a simple test row
    sheet.append_row(
        ["TEST", "Hello from Python", 123],
        value_input_option="USER_ENTERED"
    )

    print("Test row written successfully")

if __name__ == "__main__":
    main()
