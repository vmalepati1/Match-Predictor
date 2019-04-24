import requests

def tba_get_response(tba_key, router_info):
    return requests.get('https://www.thebluealliance.com/api/v3' + router_info, headers={'X-TBA-Auth-Key' : tba_key}).json()
