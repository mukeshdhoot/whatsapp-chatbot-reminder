import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- MODIFIED AUTHENTICATION FOR RENDER DEPLOYMENT ---
# 1. Retrieve the entire JSON content from the RENDER environment variable.
creds_json = os.environ.get('GOOGLE_CREDENTIALS')

if not creds_json:
    raise EnvironmentError("GOOGLE_CREDENTIALS environment variable is not set. Cannot authenticate with Google Sheets.")

# 2. Load the credentials from the JSON string.
creds_info = json.loads(creds_json)

# --- CRITICAL FIX: Ensure Private Key is correct ---
# The raw private key string must be explicitly handled.
if 'private_key' in creds_info:
    # This replaces the literal \n strings with actual line breaks for the client.
    creds_info['private_key'] = creds_info['private_key'].replace('\\n', '\n')


# 3. Use the loaded credentials to authorize the connection.
s = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, s)
client = gspread.authorize(creds)
# --- END MODIFIED AUTHENTICATION ---

# Retrieve the spreadsheet name from the environment variable (ensuring dynamic access)
spreadsheet_name = os.environ.get('SPREADSHEET_NAME', 'Whatsapp Reminders')

# Check the sheet name variable again before opening
if not spreadsheet_name:
    raise EnvironmentError("SPREADSHEET_NAME environment variable is not set.")

sheet = client.open(spreadsheet_name).sheet1
row_values=sheet.row_values(1)
col_values=sheet.col_values(1)
row_filled=len(col_values)
col_filled=len(row_values)

    
def save_reminder_date(date):
    # This part remains the same as your original logic
    sheet.update_cell(row_filled+1, 1, date)
    print("saved date!")
    return 0
    
def save_reminder_body(msg):
    # This part remains the same as your original logic
    sheet.update_cell(row_filled+1, 2, msg)
    print("saved reminder message!")
    return 0
