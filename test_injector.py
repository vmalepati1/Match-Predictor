import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Use credentials to create client and interact with Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'C:\\Users\\Vikas Malepati\\Documents\\Programming\\Private\\client_secret.json', scope)
client = gspread.authorize(creds)

# Open the simulated injection scouting sheet
simulated_scouting_sheet = client.open('Match Prediction Real-time Sandbox').get_worksheet(0)
# Open the actual scouting sheet
actual_scouting_sheet = client.open('DCMP Training Data').get_worksheet(0)

simulated_scouting_sheet.clear()

# Write header
actual_cells = actual_scouting_sheet.range('A1:V1')
simulated_scouting_sheet.update_cells(actual_cells)

match_num = 1
while True:
    actual_cells = actual_scouting_sheet.range('A{}:V{}'.format(2 + 6 * (match_num - 1), 1 + 6 * match_num))
    simulated_scouting_sheet.update_cells(actual_cells)
    match_num += 1
    time.sleep(15)
