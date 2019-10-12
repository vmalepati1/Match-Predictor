# These are the names of columns that are quantifiable and their respective functions that quantify the data they store
relevant_column_names = {
    'Robot Number ': 'any2int',
    'Match Number': 'any2int',
    "Did they show up to the match (if they don't show up, fill out 0s for all data)": 'yn2int',
    "Pass Hab Line": 'yn2int',
    "Hatches Placed on Cargo Ship (Sandstorm)": 'any2int',
    "Cargo Placed on Cargo Ship (Sandstorm)": 'any2int',
    "Hatches Placed on Rocket (Sandstorm)": 'any2int',
    "Cargo Placed on Rocket (Sandstorm)": 'any2int',
    "Hatches in Cargo Ship": 'any2int',
    "Cargo in Cargo Ship": 'any2int',
    "Hatch Panels for Level 1 of Rocket": 'any2int',
    "Cargo for Level 1 of Rocket": 'any2int',
    "Hatch Panels for Level 2 of Rocket": 'any2int',
    "Cargo for Level 2 of Rocket": 'any2int',
    "Hatch Panels for Level 3 of Rocket": 'any2int',
    "Cargo for Level 3 of Rocket": 'any2int',
    "Hatches Dropped": 'any2int',
    # "Cargo Dropped": 'any2int',
    "Level of Climb": 'level2int',
    "Assist Robots in climb (If climbed)": 'any2int',
    "Connection Status": 'connection2int',
    "Description of Speed ": 'speed2int',
    "Other": 'sentiment',
    # "Point Contribution": 'any2int'
}


def num_to_letter(q):
    q = q - 1
    result = ''
    while q >= 0:
        remain = q % 26
        result = chr(remain + 65) + result
        q = q // 26 - 1
    return result
