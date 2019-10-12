import scouting_data.sentiment.sentiment_mod as s


def yn2int(x: str):
    try:
        return 1 if x.lower() == 'yes' else 0
    except:
        return 0


def any2int(x):
    try:
        return int(x)
    except:
        return 0


def level2int(x: str):
    try:
        level_dict = {'None': 0, 'Level One': 1, 'Level Two': 2, 'Level Three': 3}
        return level_dict[x]
    except:
        return 0


def connection2int(x: str):
    try:
        connection_dict = {'No Show': 0, 'Dead entire match': 1, 'Disconnected more than once': 2,
                           'Disconnected once': 3, 'Online entire match': 4}
        return connection_dict[x]
    except:
        return 0


def speed2int(x: str):
    try:
        speed_dict = {'Slow': 0, 'Average': 1, 'Fast': 2}
        return speed_dict[x]
    except:
        return 0


def is_not_blank(s):
    return bool(s and s.strip())


def sentiment(x: str):
    try:
        if is_not_blank(x):
            return str(s.sentiment(x))
        else:
            return 0
    except:
        return 0
