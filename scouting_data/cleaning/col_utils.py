from collections import OrderedDict

# These are the names of ordered columns that are quantifiable and their respective functions that quantify the data they store

relevant_column_names = OrderedDict({
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
})

relevant_column_indices = OrderedDict({
    'Robot Number ': 2,
    'Match Number': 3,
    "Did they show up to the match (if they don't show up, fill out 0s for all data)": 4,
    "Pass Hab Line": 7,
    "Hatches Placed on Cargo Ship (Sandstorm)": 8,
    "Cargo Placed on Cargo Ship (Sandstorm)": 9,
    "Hatches Placed on Rocket (Sandstorm)": 10,
    "Cargo Placed on Rocket (Sandstorm)": 11,
    "Hatches in Cargo Ship": 12,
    "Cargo in Cargo Ship": 13,
    "Hatch Panels for Level 1 of Rocket": 14,
    "Cargo for Level 1 of Rocket": 15,
    "Hatch Panels for Level 2 of Rocket": 16,
    "Cargo for Level 2 of Rocket": 17,
    "Hatch Panels for Level 3 of Rocket": 18,
    "Cargo for Level 3 of Rocket": 19,
    "Hatches Dropped": 20,
    # "Cargo Dropped": 'any2int',
    "Level of Climb": 22,
    "Assist Robots in climb (If climbed)": 23,
    "Connection Status": 24,
    "Description of Speed ": 25,
    "Other": 26,
    # "Point Contribution": 'any2int'
})

def num_to_letter(q):
    q = q - 1
    result = ''
    while q >= 0:
        remain = q % 26
        result = chr(remain + 65) + result
        q = q // 26 - 1
    return result
