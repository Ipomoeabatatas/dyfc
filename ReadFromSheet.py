import gspread
from oauth2client.service_account import ServiceAccountCredentials


# use creds to create a client to interact with the Google Drive API


scope = ['https://spreadsheets.google.com/feeds',  'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('PythonToSheet-46f0bfa4bace.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("OneChatBotCourse-CallMe").sheet1

# Extract and print all of the values

values = ['a', 'b', 'c']
sheet.append_row(values, value_input_option='RAW')
# list_of_hashes = sheet.get_all_records()
# print(list_of_hashes)
