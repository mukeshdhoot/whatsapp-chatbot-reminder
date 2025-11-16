import os
import json
import gspread
from google.oauth2.service_account import Credentials
import base64 # Import base64 for decoding check

# --- FINAL CLEAN AUTHENTICATION ---
try:
    # Read individual key components from the environment variables.
    creds_info = {
        "type": "service_account",
        "project_id": os.environ.get('PROJECT_ID').strip(), # .strip() added
        "private_key_id": os.environ.get('PRIVATE_KEY_ID').strip(), # .strip() added
        "client_email": os.environ.get('CLIENT_EMAIL').strip(), # .strip() added
        "client_id": os.environ.get('CLIENT_ID').strip(), # .strip() added
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL').strip(), # .strip() added
        
        # CRITICAL FIX: The key must be stripped of whitespace.
        "private_key": os.environ.get('PRIVATE_KEY_RAW').strip().replace('\\n', '\n'), # .strip() added
    }

    # Verify essential variables are present before proceeding
    if not all(creds_info.get(k) for k in ['project_id', 'private_key', 'client_email']):
         raise EnvironmentError("Missing essential Google credential components in environment variables.")

    # Use the modern Google Auth Credentials
    s = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=s)
    client = gspread.authorize(creds)

except Exception as e:
    # If the authentication fails at any point, stop the app and show a clear error.
    raise EnvironmentError(f"CRITICAL AUTHENTICATION FAILURE: Check all 8 Google credential variables. Error: {e}")

# --- END FINAL CLEAN AUTHENTICATION ---

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
