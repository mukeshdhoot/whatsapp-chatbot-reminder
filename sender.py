import os
import json
import datetime
import gspread
from twilio.rest import Client

# --- CONFIGURATION ---
# Define the time format used in your Google Sheet (e.g., '10 AM', '4:30 PM')
# This script assumes a 12-hour clock format followed by AM/PM.
TIME_FORMAT = "%I %p" 
# The index of the column in your sheet for each data point (starting count at 1)
COL_DATE = 1
COL_NUMBER = 2
COL_MESSAGE = 3
COL_TIME = 4
COL_STATUS = 5 

# --- TWILIO INITIALIZATION ---
try:
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    # You must provide the Twilio WhatsApp number (e.g., 'whatsapp:+14155238886')
    TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") 
    
    # Initialize the Twilio client for sending messages
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

except Exception as e:
    print(f"ERROR: Could not initialize Twilio client. Check TWILIO_SID/TOKEN. Error: {e}")
    # Exit the script if Twilio credentials are bad
    exit(1)


# --- GOOGLE SHEETS INITIALIZATION ---
def initialize_gsheets():
    """Initializes GSheets authentication and returns the worksheet object."""
    try:
        # 1. Construct the Google Service Account credentials dictionary (using the same logic as gsheet_func.py)
        GOOGLE_CREDS = {
            "type": "service_account",
            "project_id": os.environ.get('PROJECT_ID', '').strip(),
            "private_key_id": os.environ.get('PRIVATE_KEY_ID', '').strip(),
            # CRITICAL FIX: Ensure newlines are preserved for the private key
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
        
        # 2. Authenticate and open the sheet
        gc = gspread.service_account_from_dict(GOOGLE_CREDS)
        spreadsheet = gc.open(SPREADSHEET_NAME)
        return spreadsheet.sheet1
    
    except Exception as e:
        print(f"CRITICAL ERROR: Could not initialize Google Sheets. Check credentials/sharing. Error: {e}")
        exit(1)


# --- MAIN SCHEDULER LOGIC ---
def send_due_reminders(worksheet):
    """Checks the sheet for due reminders and sends them via Twilio."""
    
    # Get all records where status is 'Pending'
    pending_reminders = worksheet.get_all_records()
    
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    print(f"Scheduler running at: {now.strftime('%H:%M:%S')}")
    
    messages_sent = 0

    for index, reminder in enumerate(pending_reminders):
        # Index in the sheet is 2 + loop index (Row 1 is headers, Row 2 is the first record)
        row_num = index + 2 
        
        # Check if the message is already sent
        if reminder.get('Status') != 'Pending':
            continue

        try:
            # Combine current date with the time string from the sheet to get a full datetime object
            time_str = reminder.get('Time')
            reminder_time = datetime.datetime.strptime(time_str, TIME_FORMAT).replace(
                year=now.year, month=now.month, day=now.day
            )

            # Check if the reminder time is now or in the past
            if reminder_time <= now:
                
                # 1. SEND THE MESSAGE VIA TWILIO
                reminder_text = f"REMINDER: It's time to {reminder.get('Reminder Messages')}."
                recipient_number = reminder.get('Date') # The first column holds the WhatsApp number

                message = twilio_client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    body=reminder_text,
                    to=recipient_number
                )
                print(f"SENT: {reminder_text} to {recipient_number}")

                # 2. UPDATE THE STATUS IN GOOGLE SHEET
                # Update the Status column (Column 5) for this row
                worksheet.update_cell(row_num, COL_STATUS, 'Sent')
                messages_sent += 1

        except Exception as e:
            print(f"FAILED to process reminder in row {row_num}: {e}")

    print(f"Scheduler finished. Total messages sent: {messages_sent}")


if __name__ == "__main__":
    # Ensure the script runs only when executed directly
    sheets_worksheet = initialize_gsheets()
    send_due_reminders(sheets_worksheet)
