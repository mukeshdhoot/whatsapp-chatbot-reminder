import os
import json
import gspread
from google.oauth2.service_account import Credentials # <--- NEW AUTH LIBRARY
# from oauth2client.service_account import ServiceAccountCredentials # <--- DELETED

# --- FINAL MODIFIED AUTHENTICATION FOR RENDER DEPLOYMENT ---
try:
    # 1. Retrieve the entire JSON content from the RENDER environment variable.
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')

    if not creds_json:
        raise EnvironmentError("GOOGLE_CREDENTIALS environment variable is not set. Cannot authenticate with Google Sheets.")

    # 2. Load the credentials from the JSON string.
    creds_info = json.loads(creds_json)
    
    # CRITICAL FIX: The older library (oauth2client) required complicated fixing. 
    # The modern google-auth library handles the escaping automatically if the JSON is clean.

    # 3. Use the modern Google Auth Credentials.from_service_account_info method
    s = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=s)
    client = gspread.authorize(creds)

except Exception as e:
    print(f"Authentication Failed: {e}")
    # Raise a specific error to halt execution if auth fails
    raise EnvironmentError(f"CRITICAL AUTHENTICATION FAILURE: Check GOOGLE_CREDENTIALS value. {e}")

# --- END MODIFIED AUTHENTICATION ---

# Retrieve the spreadsheet name
spreadsheet_name = os.environ.get('SPREADSHEET_NAME', 'Whatsapp Reminders')

sheet = client.open(spreadsheet_name).sheet1
row_values=sheet.row_values(1)
col_values=sheet.col_values(1)
row_filled=len(col_values)
col_filled=len(row_values)

def save_reminder_date(date):
    sheet.update_cell(row_filled+1, 1, date)
    print("saved date!")
    return 0
    
def save_reminder_body(msg):
    sheet.update_cell(row_filled+1, 2, msg)
    print("saved reminder message!")
    return 0
