from ping_tba_api import *
import numpy as np
import sys

def create_dataset(out_filepath : str, tba_api_key : str, year : int):
    # Dataset return lists
    x = []
    y = []

    # Get all events that happened during the specified year
    events = tba_get_response(tba_api_key, '/events/' + str(year))

    for event in events:
        event_key = event['key']
        
        for match in tba_get_response(tba_api_key, '/event/' + event_key + '/matches'):
            # List of team keys
            red_team_keys = match['alliances']['red']['team_keys']
            blue_team_keys = match['alliances']['blue']['team_keys']

            # Red statistics for the match
            red_input = []

            # Blue statistics for the match
            blue_input = []

            # If teams were absent or something else, skip this match
            try:
                # Team status is nothing but the statistics for the match for the team (ex. how many hatches or cargo placed in Deep Space)
                for team_key in red_team_keys:
                    team_status = tba_get_response(tba_api_key, '/team/' + team_key + '/event/' + event_key + '/status')
                    red_input.append(team_status['qual']['ranking']['sort_orders'])

                for team_key in blue_team_keys:
                    team_status = tba_get_response(tba_api_key, '/team/' + team_key + '/event/' + event_key + '/status')
                    blue_input.append(team_status['qual']['ranking']['sort_orders'])
            except:
                continue

            # Flatten red input and blue input arrays to contain all three team statistics
            
            red_input = red_input[0] + red_input[1] + red_input[2]
            blue_input = blue_input[0] + blue_input[1] + blue_input[2]
            red_output = match['alliances']['red']['score']
            blue_output = match['alliances']['blue']['score']

            # Input to training contains the statistics of the corresponding alliance color statistics
            # to output followed by the opposing alliance statistics
            x.append(red_input + blue_input)
            y.append(red_output)
            
            x.append(blue_input + red_input)
            y.append(blue_output)
        break

    # Save our dataset to the specified file path
    np.savez(out_filepath, x=np.array(x), y=np.array(y))

if sys.argv[1].lower() == 'usage':
    print('Usage: create_dataset.py out_filepath tba_api_key year')
    exit()

create_dataset(sys.argv[1], sys.argv[2], int(sys.argv[3]))
