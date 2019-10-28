from collections import OrderedDict

import tbapy

tba = tbapy.TBA('1wui0Dih1NifktYrjoXW2hWaMY9XwTfRXaM985Eringd4jeU2raza2nSLXfiALPM')

events = tba.team_events(2974, 2019)

event_dict_unordered = dict((x['start_date'], x) for x in events)
event_dict_ordered = OrderedDict(sorted(event_dict_unordered.items(), key=lambda t: t[0]))
last_event_key = list(event_dict_ordered.items())[-1][1]['key']

print(tba.team_status(2974, last_event_key)['qual']['ranking']['sort_orders'])
