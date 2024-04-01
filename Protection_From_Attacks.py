'''
sql_injection_possible_codes = ["OR", "UNION", "DROP", "DELETE", "TRUNCATE", "SELECT", "UPDATE", "INSERT", "LIKE"]


"""
Returns True when there's a code of sql injection, and False when the msg in clean.
"""
def check_for_sql_injection(msg):
    for i in sql_injection_possible_codes:
        if i in msg:
            return True
    return False
'''

MAX_LENGTH_OF_MSG = 300
"""
Returns True when the msg is too long, and False when the msg in ok.
"""
def check_length_of_msg(msg):
    if len(msg) > MAX_LENGTH_OF_MSG:
        return True
    return False
