import os
import datetime
import gspread
import pytz # <-- NEW IMPORT
from twilio.rest import Client

# --- CONFIGURATION (TIME ZONE ADDED) ---
TIME_FORMAT = "%I:%M %p" # Corrected format for "8:22 AM"
LOCAL_TIMEZONE = pytz.timezone('Asia/Kolkata') # Your local timezone (IST)
UTC_TIMEZONE = pytz.utc # Server timezone

# Define the exact header row names as they appear in your Google Sheet (Row 1).
EXPECTED_HEADERS = ['Date', 'Reminder Messages', 'Time', 'Status'] 
COL_DATE = 'Date'
COL_MESSAGE = 'Reminder Messages'
COL_TIME = 'Time'
COL_STATUS = 'Status' 

# ... (The rest of the Twilio and GSheets Initialization remains the same) ...

# --- GOOGLE SHEETS INITIALIZATION ---
def initialize_gsheets():
    """Initializes GSheets authentication and returns the worksheet object."""
    try:
        # ... (Google_CREDS loading remains the same) ...
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
        gc = gspread.service_account_from_dict(GOOGLE_CREDS)
        spreadsheet = gc.open(SPREADSHEET_NAME)
        return spreadsheet.sheet1
    
    except Exception as e:
        print(f"CRITICAL ERROR: Could not initialize Google Sheets. Error: {e}")
        exit(1)

# --- MAIN SCHEDULER LOGIC ---
def send_due_reminders(worksheet):
    """Checks the sheet for due reminders and sends them via Twilio."""
    
    pending_reminders = worksheet.get_all_records(expected_headers=EXPECTED_HEADERS)
    
    # Get the current time localized to your IST timezone
    now_utc = datetime.datetime.now(UTC_TIMEZONE)
    now_local = now_utc.astimezone(LOCAL_TIMEZONE).replace(second=0, microsecond=0)
    
    # Find the column index for status update
    status_col_index = worksheet.find(COL_STATUS).col
    
    print(f"Scheduler running. Local Time (IST): {now_local.strftime('%H:%M:%S')}")
    
    messages_sent = 0

    for index, reminder in enumerate(pending_reminders):
        row_num = index + 2 
        
        if reminder.get(COL_STATUS) != 'Pending':
            continue

        try:
            # 1. Parse the time string from the sheet and localize it to IST
            time_str = reminder.get(COL_TIME)
            
            # NOTE: We assume time_str is now in the format "8:22 AM" (with colon and space)
            reminder_time_naive = datetime.datetime.strptime(time_str, TIME_FORMAT).replace(
                year=now_local.year, month=now_local.month, day=now_local.day
            )
            
            # Localize the reminder time to IST
            reminder_time_local = LOCAL_TIMEZONE.localize(reminder_time_naive)

            # 2. Check if the reminder time has been met or passed
            if reminder_time_local <= now_local:
                
                # 3. SEND THE MESSAGE VIA TWILIO
                reminder_text = f"REMINDER: It's time to {reminder.get(COL_MESSAGE)}."
                recipient_number = reminder.get(COL_DATE).strip()

                # Twilio send logic here...
                # message = twilio_client.messages.create(...)

                print(f"SENT: {reminder_text} to {recipient_number}")

                # 4. UPDATE THE STATUS IN GOOGLE SHEET
                worksheet.update_cell(row_num, status_col_index, 'Sent')
                messages_sent += 1

        except Exception as e:
            print(f"FAILED to process reminder in row {row_num}: {e}")

    print(f"Scheduler finished. Total messages sent: {messages_sent}")


if __name__ == "__main__":
    sheets_worksheet = initialize_gsheets()
    send_due_reminders(sheets_worksheet)
