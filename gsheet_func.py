import os
import json
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread

# --- 1. CREDENTIALS AND AUTHENTICATION ---
# Safely load all credentials from environment variables.
try:
    # 1.1. Construct the Google Service Account credentials dictionary
    # CRITICAL FIX: The .replace('\\n', '\n') ensures the private key's newlines are correctly parsed.
    GOOGLE_CREDS = {
        "type": "service_account",
        "project_id": os.environ.get('PROJECT_ID', '').strip(),
        "private_key_id": os.environ.get('PRIVATE_KEY_ID', '').strip(),
        "private_key": os.environ.get('PRIVATE_KEY_RAW', '').strip().replace('\\n', '\n'),
        "client_email": os.environ.get('CLIENT_EMAIL', '').strip(),
        "client_id": os.environ.get('CLIENT_ID', '').strip(),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL', '').strip(),
        "universe_domain": "googleapis.com"
    }

    SPREADSHEET_NAME = os.environ.get('SPREADSHEET_NAME')
    
    # 1.2. Authenticate and open the sheet (This fails if creds are bad or sheet not shared)
    gc = gspread.service_account_from_dict(GOOGLE_CREDS)
    spreadsheet = gc.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.sheet1
    
except Exception as e:
    # If the app crashes here, check the 9 variables one last time, or the GSheet sharing.
    raise EnvironmentError(f"CRITICAL AUTHENTICATION FAILURE: Check all 9 credentials, their spelling/case, and GSheet sharing. Error: {e}")

# --- 2. APPLICATION INITIALIZATION ---
# VITAL FIX: The name MUST be 'app' to match the Procfile command 'gsheet_func:app'.
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

    # 3.2. Check for reminder command (Simple parsing logic)
    if incoming_msg.startswith('remind me to'):
        try:
            # Simple parsing: Find 'at' to separate task and time
            parts = incoming_msg.split(' at ', 1)
            task = parts[0].replace('remind me to', '').strip()
            time_str = parts[1].strip()

            # 3.3. Add the reminder to the Google Sheet
            # Row format: [Sender_Number, Task, Time, Status]
            worksheet.append_row([sender_id, task, time_str, 'Pending'])
            
            response_text = f"Got it! I've set a reminder to '{task}' for {time_str}."
        
        except IndexError:
            # Failed to parse the 'at' keyword or the time
            response_text = "Please specify the task AND the time. Example: 'remind me to clean the kitchen at 8 PM'."
        
        except Exception as sheet_error:
            # Failed to write to the sheet (e.g., connection timed out)
            response_text = f"Sorry, I couldn't save the reminder. The app failed to write the row."
    
    # 3.4. Send the final response back to the sender
    msg.body(response_text)

    # Twilio automatically handles sending the TwiML response back to the sender.
    return str(resp)

# --- 4. OPTIONAL: Local Run Command (Ignored by Railway) ---
if __name__ == '__main__':
    # This runs only when the file is executed directly (not by gunicorn)
    app.run(debug=True)
