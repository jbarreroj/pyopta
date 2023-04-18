from datetime import datetime

# Define some constants to use throughout the code
UNDEFINED_INT = -9999
UNDEFINED_FLOAT = -9999.9
UNDEFINED_DATE = datetime.strptime("9999-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")

# Define a dictionary of operators and their descriptions
OPERATORS = {
    "EQ":"equal",
    "NEQ":"not_equal",
    "LT":"less_than",
    "LTE":"less_than_or_equal",
    "GT":"greater_than",
    "GTE":"greater_than_or_equal",
    "BW":"between",
    "IN":"in",
    "NIN":"not_in",
    "QIN":"qualifier_in",
    "QNIN":"qualifiers_not_in"
}

# Define a dictionary of event IDs and their descriptions
EVENT_IDS = {
    "Pass": 1,
    "Offside Pass": 2,
    "Take On": 3,
    "Free kick": 4,
    "Out": 5,
    "Corner": 6,
    "Tackle": 7,
    "Interception": 8,
    "Turnover": 9,
    "Save": 10,
    "Claim": 11,
    "Clearance": 12,
    "Miss": 13,
    "Post": 14,
    "Attempt Saved": 15,
    "Goal": 16,
    "Card": 17,
    "Player off": 18,
    "Player on": 19,
    "Player retired": 20,
    "Player returns": 21,
    "Player becomes goalkeeper": 22,
    "Goalkeeper becomes player": 23,
    "Condition change": 24,
    "Official change": 25,
    "Possession": 26,
    "Start delay": 27,
    "End delay": 28,
    "Temporary stop": 29,
    "End": 30,
    "Picked an orange": 31,
    "Start": 32,
    "Start/End canceling": 33,
    "Team set up": 34,
    "Player changed position": 35,
    "Player changed Jersey number": 36,
    "Collection End": 37,
    "Temp_Goal": 38,
    "Temp_Attempt": 39,
    "Formation change": 40,
    "Punch": 41,
    "Good skill": 42,
    "Deleted event": 43,
    "Aerial": 44,
    "Challenge": 45,
    "Postponed": 46,
    "Rescinded card": 47,
    "Provisional lineup": 48,
    "Ball recovery": 49,
    "Dispossessed": 50,
    "Keeper pick-up": 52,
    "Cross not claimed": 53,
    "Smother": 54,
    "Offside provoked": 55,
    "Error": 51,
    "Shot faced": 58,
    "Shield ball oop": 56,
    "Foul throw in": 57,
    "Keeper Sweeper": 59,
    "Event placeholder": 62,
    "Chance Missed": 60,
    "Ball touch": 61,
    "Temp_Save": 63,
    "Resume": 64,
    "Contentious referee decision": 65  
}

# Define a dictionary of qualifier IDs and their descriptions
QUALIFIER_IDS = {
    "Long ball": 1,
    "Cross": 2,
    "Head pass": 3,
    "Through ball": 4,
    "Free kick taken": 5,
    "Corner taken": 6,
    "Players caught offside": 7,
    "Goal disallowed": 8,
    "Penalty": 9,
    "Hand": 10,
    "6-seconds violation": 11,
    "Dangerous play": 12,
    "Foul": 13,
    "Last line": 14,
    "Head": 15,
    "Small box-centre": 16,
    "Box-centre": 17,
    "Out of box-centre": 18,
    "35+ centre": 19,
    "Right footed": 20,
    "Other body part": 21,
    "Regular play": 22,
    "Fast break": 23,
    "Set piece": 24,
    "From corner": 25,
    "Free kick": 26,
    "own goal ": 28,
    "Assisted": 29,
    "Involved": 30,
    "Yellow Card": 31,
    "Second yellow": 32,
    "Red Card": 33,
    "Referee abuse": 34,
    "Argument": 35,
    "Fight": 36,
    "Time wasting": 37,
    "Excessive celebration": 38,
    "Crowd interaction": 39,
    "Other reason": 40,
    "Injury": 41,
    "Tactical": 42,
    "Player Position": 44,
    "Temperature": 45,
    "Conditions": 46,
    "Field Pitch": 47,
    "Lightings": 48,
    "Attendance figure": 49,
    "Official position": 50,
    "Official Id": 51,
    "Injured player id": 53,
    "End cause": 54,
    "Related event ID": 55,
    "Zone": 56,
    "End type": 57,
    "Jersey Number": 59,
    "Small box-right": 60,
    "Small box-left": 61,
    "Box-deep right": 62,
    "Box-right": 63,
    "Box-left": 64,
    "Box-deep left": 65,
    "Out of box-deep right": 66,
    "Out of box-right": 67,
    "Out of box-left": 68,
    "Out of box-deep left": 69,
    "35+ right": 70,
    "35+ left": 71,
    "Left footed": 72,
    "Left": 73,
    "High": 74,
    "Right": 75,
    "Low Left": 76,
    "High Left": 77,
    "Low Centre": 78,
    "High Centre": 79,
    "Low Right": 80,
    "High Right": 81,
    "Blocked": 82,
    "Close Left": 83,
    "Close Right": 84,
    "Close High": 85,
    "Close Left and High": 86,
    "Close Right and High": 87,
    "High claim": 88,
    "1 on 1": 89,
    "Deflected save": 90,
    "Dive and deflect": 91,
    "Catch": 92,
    "Dive and catch": 93,
    "Def block": 94,
    "Back pass": 95,
    "Corner situation": 96,
    "Direct free": 97,
    "Six Yard Blocked": 100,
    "Saved Off Line": 101,
    "Goal Mouth Y Coordinate": 102,
    "Goal Mouth Z Coordinate": 103,
    "Attacking Pass": 106,
    "Throw In": 107,
    "Volley": 108,
    "Overhead": 109,
    "Half Volley": 110,
    "Diving Header": 111,
    "Scramble": 112,
    "Strong": 113,
    "Weak": 114,
    "Rising": 115,
    "Dipping": 116,
    "Lob": 117,
    "One Bounce": 118,
    "Few Bounces": 119,
    "Swerve Left": 120,
    "Swerve Right": 121,
    "Swerve Moving": 122,
    "Keeper Throw": 123,
    "Goal Kick": 124,
    "Punch": 128,
    "Team Formation": 130,
    "Team Player Formation": 131,
    "Dive": 132,
    "Deflection": 133,
    "Far Wide Left": 134,
    "Far Wide Right": 135,
    "Keeper Touched": 136,
    "Keeper Saved": 137,
    "Hit Woodwork": 138,
    "Own Player": 139,
    "Pass End X": 140,
    "Pass End Y": 141,
    "Deleted Event Type": 144,
    "Formation slot": 145,
    "Blocked X Coordinate": 146,
    "Blocked Y Coordinate": 147,
    "Not past goal line": 153,
    "Intentional Assist": 154,
    "Chipped": 155,
    "Lay-off": 156,
    "Launch": 157,
    "Persistent Infringement": 158,
    "Foul and Abusive Language": 159,
    "Throw In set piece": 160,
    "Encroachment": 161,
    "Leaving field": 162,
    "Entering field": 163,
    "Spitting": 164,
    "Professional foul": 165,
    "Handling on the line": 166,
    "Out of play": 167,
    "Flick-on": 168,
    "Leading to attempt": 169,
    "Leading to goal": 170,
    "Rescinded Card": 171,
    "No impact on timing": 172,
    "Parried safe": 173,
    "Parried danger": 174,
    "Fingertip": 175,
    "Caught": 176,
    "Collected": 177,
    "Standing": 178,
    "Diving": 179,
    "Stooping": 180,
    "Reaching": 181,
    "Hands": 182,
    "Feet": 183,
    "Dissent": 184,
    "Blocked cross": 185,
    "Scored": 186,
    "Saved": 187,
    "Missed": 188,
    "Player Not Visible": 189,
    "From shot off target": 190,
    "Off the ball foul": 191,
    "Block by hand": 192,
    "Captain": 194,
    "Pull Back": 195,
    "Switch of play": 196,
    "Team kit": 197,
    "GK hoof": 198,
    "Gk kick from hands": 199,
    "Referee stop": 200,
    "Referee delay": 201,
    "Weather problem": 202,
    "Crowd trouble": 203,
    "Fire": 204,
    "Object thrown on pitch": 205,
    "Spectator on pitch": 206,
    "Awaiting officials decision": 207,
    "Referee Injury": 208,
    "Game end": 209,
    "Assist": 210,
    "Overrun": 211,
    "Length": 212,
    "Angle": 213,
    "Big Chance": 214,
    "Individual Play": 215,
    "2nd related event ID": 216,
    "2nd assited": 217,
    "2nd assist": 218,
    "Players on both posts": 219,
    "Player on near post": 220,
    "Player on far post": 221,
    "No players on posts": 222,
    "Inswinger": 223,
    "Outswinger": 224,
    "Straight": 225,
    "Suspended": 226,
    "Resume": 227,
    "Own shot blocked": 228,
    "Post match complete": 229
}
