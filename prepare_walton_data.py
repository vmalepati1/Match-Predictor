import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

# Use credentials to create client and interact with Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/User/Documents/Programming/Private/client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Match Scouting Form (Dalton) (Responses)').get_worksheet(0)
