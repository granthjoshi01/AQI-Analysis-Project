import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")
SPREADSHEET_NAME = "aqi_live_data"
WORKSHEET_NAME = "aqi_cleaned_data"


def write_dataframe_to_sheet(df: pd.DataFrame):
    """
    Write the AQI dataset to Google Sheets as a full refresh.

    The sheet is treated as a read-only mirror of the local CSV:
    - existing content is cleared
    - headers are written
    - all rows are written in newest-first order
    """

    # Google Sheets is strict about JSON values.
    # Pandas can contain NaN / NaT / nullable dtypes that the API rejects,
    # so we normalise everything to plain Python objects here.
    df = df.copy()
    df = df.astype(object)
    df = df.replace([float("inf"), float("-inf")], None)
    df = df.where(pd.notnull(df), None)

    # Make sure the newest records always appear first in the sheet
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp", ascending=False)

    for col in df.columns:
        # Convert any datetime-like columns to strings (Sheets can't store datetime objects)
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        elif df[col].apply(lambda x: isinstance(x, datetime.date)).any():
            df[col] = df[col].apply(
                lambda x: x.strftime("%Y-%m-%d") if isinstance(x, datetime.date) else x
            )

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)

    # Create the worksheet once if it doesn't already exist
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(df.columns)
        )

    # Clear and rewrite the sheet so it exactly matches the local CSV
    worksheet.clear()

    # Write header
    worksheet.append_row(df.columns.tolist(), value_input_option="USER_ENTERED")

    # Write all data rows
    if not df.empty:
        worksheet.append_rows(df.values.tolist(), value_input_option="USER_ENTERED")
