from ping_tba_api import *

def create_dataset(tba_api_key, year):
    events = tba_get_response(tba_api_key, '/events/' + str(year))

    for event in events:
        event_key = event['key']

create_dataset('1wui0Dih1NifktYrjoXW2hWaMY9XwTfRXaM985Eringd4jeU2raza2nSLXfiALPM', 2016)
