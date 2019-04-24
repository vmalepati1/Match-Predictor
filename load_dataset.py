from ping_tba_api import *

def create_dataset(tba_api_key, year):
    x = []
    Y = []
    
    events = tba_get_response(tba_api_key, '/events/' + str(year))

    for event in events:
        event_key = event['key']

        for match in tba_get_response(tba_api_key, '/event/' + event_key + '/matches'):
            red_team_keys = match['alliances']['red']['team_keys']
            blue_team_keys = match['alliances']['blue']['team_keys']

            

TBA_KEY = '1wui0Dih1NifktYrjoXW2hWaMY9XwTfRXaM985Eringd4jeU2raza2nSLXfiALPM'
create_dataset(TBA_KEY, 2016)
