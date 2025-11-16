import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- FINAL MODIFIED AUTHENTICATION FOR RENDER DEPLOYMENT ---
# We read individual components from environment variables to bypass base64 corruption.
try:
    creds_info = {
        "type": "service_account",
        "project_id": os.environ.get('PROJECT_ID'),
        "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
        "private_key": os.environ.get('PRIVATE_KEY_RAW').replace('\\n', '\n'),
        "client_email": os.environ.get('CLIENT_EMAIL'),
        "client_id": os.environ.get('CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL')
    }

except AttributeError:
    # This will catch if any environment variable is missing, providing a clearer error message.
    raise EnvironmentError("One or more Google credentials environment variables are missing. Please check PROJECT_ID, PRIVATE_KEY_RAW, etc.")


# Use the loaded credentials to authorize the connection.
s = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, s)
client = gspread.authorize(creds)
# --- END MODIFIED AUTHENTICATION ---

# Retrieve the spreadsheet name
spreadsheet_name = os.environ.get('SPREADSHEET_NAME', 'Whatsapp Reminders')

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
