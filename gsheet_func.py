import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- MODIFIED AUTHENTICATION FOR RENDER DEPLOYMENT ---
# 1. Retrieve the JSON key content from the RENDER environment variable.
#    The variable name 'GOOGLE_CREDENTIALS' must match the key you set on Render.
creds_json = os.environ.get('GOOGLE_CREDENTIALS')

# 2. Check if the variable is set; if not, the environment is wrong.
if not creds_json:
    raise EnvironmentError("GOOGLE_CREDENTIALS environment variable is not set. Cannot authenticate with Google Sheets.")

# 3. Load the credentials from the JSON string.
creds_info = json.loads(creds_json)

# 4. Use the loaded credentials to authorize the connection.
s = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
# We use from_json_keyfile_dict instead of from_json_keyfile_name
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, s)
client = gspread.authorize(creds)
# --- END MODIFIED AUTHENTICATION ---

# Retrieve the spreadsheet name from the environment variable (ensuring dynamic access)
spreadsheet_name = os.environ.get('SPREADSHEET_NAME', 'Whatsapp Reminders')

sheet = client.open(spreadsheet_name).sheet1
row_values=sheet.row_values(1)
col_values=sheet.col_values(1)
row_filled=len(col_values)
col_filled=len(row_values)

    
def save_reminder_date(date):
    # NOTE: The row_filled variable is static upon script startup. 
    # For a production app, this should be re-calculated inside the function or use append_row.
    # We maintain the original code's structure here for simplicity.
    sheet.update_cell(row_filled+1, 1, date)
    print("saved date!")
    return 0
    
def save_reminder_body(msg):
    sheet.update_cell(row_filled+1, 2, msg)
    print("saved reminder message!")
    return 0
