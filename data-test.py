import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_ID = '161JVy5kmupt8sgERs7n3gx-DBAk1KQnt1712rrLwmac'  # Replace with your ID
sheet = client.open_by_key(SPREADSHEET_ID)
print(f"Worksheets: {[ws.title for ws in sheet.worksheets()]}")

for ws in sheet.worksheets():
    print(f"\n{ws.title}:")
    data = ws.get_all_values()
    for row in data[:10]:  # First 10 rows
        print(row)