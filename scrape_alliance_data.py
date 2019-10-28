import tbapy


def scrape_alliance_data(tba_key: str, year: int, event_name: str, match_num: int, match_type='qm', round=False):
    '''Given TBA-Authentication key, Competition year, event name, and match number, queries TBA for basic match data
    of each team in the match. '''
    tba = tbapy.TBA(tba_key)
    year = int(year)
    match_num = int(match_num)
    round = int(round)
    event_key = ''
    red_data = []
    blue_data = []

    for event in tba.events(year):
        if event.name == event_name:
            event_key = event.key
            break

    red_alliance_teams = tba.match(year=year, event=event_key, type=match_type, number=match_num)['alliances']['red'][
        'team_keys'] if match_type == 'qm' else \
        tba.match(year=year, event=event_key, type=match_type, number=match_num, round=round)['alliances']['red'][
            'team_keys']
    blue_alliance_teams = tba.match(year=year, event=event_key, type=match_type, number=match_num)['alliances']['blue'][
        'team_keys'] if match_type == 'qm' else \
        tba.match(year=year, event=event_key, type=match_type, number=match_num, round=round)['alliances']['blue'][
            'team_keys']

    for team in red_alliance_teams:
        team_data = tba.team_status(team, event_key)['qual']['ranking']['sort_orders']
        red_data.append(team_data)
    for team in blue_alliance_teams:
        team_data = tba.team_status(team, event_key)['qual']['ranking']['sort_orders']
        blue_data.append(team_data)

    return red_data, blue_data
