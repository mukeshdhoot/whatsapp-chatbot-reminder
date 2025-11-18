import os
import json
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread

# --- 1. CREDENTIALS AND AUTHENTICATION (The Fix for the 'NoneType' crash) ---
# We use os.environ.get(VAR, default) to prevent crashing if a variable is missing.
try:
    # Safely load the Google Service Account credentials from environment variables
    # The .strip() is safe here because we provide a default empty string ''
    GOOGLE_CREDS = {
        "type": "service_account",
        "project_id": os.environ.get('PROJECT_ID', '').strip(),
        "private_key_id": os.environ.get('PRIVATE_KEY_ID', '').strip(),
        "private_key": os.environ.get('PRIVATE_KEY_RAW', '').strip(),
        "client_email": os.environ.get('CLIENT_EMAIL', '').strip(),
        "client_id": os.environ.get('CLIENT_ID', '').strip(),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL', '').strip(),
        "universe_domain": "googleapis.com"
    }

    SPREADSHEET_NAME = os.environ.get('SPREADSHEET_NAME')
    
    # 2. Authenticate with Google Sheets
    gc = gspread.service_account_from_dict(GOOGLE_CREDS)
    spreadsheet = gc.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.sheet1
    
except Exception as e:
    # This will catch any errors during credential loading or GSheets connection
    raise EnvironmentError(f"CRITICAL AUTHENTICATION FAILURE: Check all 8 Google credential variables or Sheet name/sharing. Error: {e}")

# --- 2. APPLICATION INITIALIZATION (The Fix for the 'app' crash) ---
# VITAL FIX: The name of the Flask application variable MUST be 'app' to match the Procfile.
app = Flask(__name__) 

# --- 3. TWILIO WEBHOOK ROUTE AND LOGIC ---
@app.route('/webhook', methods=['POST'])
def webhook():
    # 3.1. Get the incoming message and phone number
    incoming_msg = request.values.get('Body', '').lower()
    sender_id = request.values.get('From', '') # The sender's WhatsApp number

    resp = MessagingResponse()
    msg = resp.message()
    
    response_text = "I didn't understand that. To set a reminder, please use the format: 'remind me to [TASK] at [TIME]'."

    # 3.2. Check for reminder command (Simplified parsing)
    if incoming_msg.startswith('remind me to'):
        try:
            # Simple parsing: Find 'at' to separate task and time
            parts = incoming_msg.split(' at ', 1)
            task = parts[0].replace('remind me to', '').strip()
            time_str = parts[1].strip()

            # 3.3. Add the reminder to the Google Sheet
            worksheet.append_row([sender_id, task, time_str, 'Pending'])
            
            response_text = f"Got it! I've set a reminder to '{task}' for {time_str}."
        
        except IndexError:
            # Failed to parse "at" or the time
            response_text = "Please specify the task AND the time. Example: 'remind me to clean the kitchen at 8 PM'."
        
        except Exception as sheet_error:
            # Failed to write to the sheet (e.g., worksheet is full, network error)
            # This is where the sharing error would be caught now
            response_text = f"Sorry, I couldn't save the reminder. Check the app logs for the error: {sheet_error}"
    
    # 3.4. Send the final response back to the sender
    msg.body(response_text)

    # VITAL FIX: Ensure the reply goes back to the sender, not the Twilio number
    # Twilio automatically handles sending the TwiML response back to the 'From' number.
    return str(resp)

# --- 4. OPTIONAL: Local Run Command (Ignored by Railway) ---
if __name__ == '__main__':
    # When running locally, Flask runs on 5000. Railway ignores this block.
    # The debug=True setting is helpful for local development.
    app.run(debug=True)
