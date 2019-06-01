from ping_tba_api import *

def scrape_alliance_data(tba_api_key : str, year : int, event_name : str, current_match : int, match_type='qm'):
    event_key = ''
    
    # Find the specified event key from event name and year
    for event in tba_get_response(tba_api_key, '/events/' + str(year)):
        if event['name'] == event_name:
            event_key = event['key']
            break

    

    # Search for the correct match and return data from each alliance

    current_finds = 0
    
    for match in tba_get_response(tba_api_key, '/event/' + event_key + '/matches'):
        if match['comp_level'] == match_type:
            current_finds += 1
            
            if match['match_number'] == current_match and match_type == 'qm' or current_finds == current_match and match_type != 'qm':
                red_team_keys = match['alliances']['red']['team_keys']
                blue_team_keys = match['alliances']['blue']['team_keys']

                # Red statistics for the match
                red_input = []

                # Blue statistics for the match
                blue_input = []

                for team_key in red_team_keys:
                    team_status = tba_get_response(tba_api_key, '/team/' + team_key + '/event/' + event_key + '/status')
                    red_input.append(team_status['qual']['ranking']['sort_orders'])

                for team_key in blue_team_keys:
                    team_status = tba_get_response(tba_api_key, '/team/' + team_key + '/event/' + event_key + '/status')
                    blue_input.append(team_status['qual']['ranking']['sort_orders'])

                return red_input, blue_input

    # Error in finding the match
    return None, None
