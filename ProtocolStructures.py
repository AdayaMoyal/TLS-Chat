
message_codes = {204:"chachaWithoutSendmsg", 205:"aesgcmWithSendmsg", 206:"aesgcmWithoutSendmsg", 207:"chachaWithSendmsg"}

"""Create the general_message_structure1- one of the general structures to pass info from client to server (and then p2p)
    :param code: the code of the message, each code means something else
    :param msg: the message that one of the sides wants to send to the other
    :type code: int
    :type msg: string
    :return: a msg to send to the other side
    :rtype: string
    """

def users_message_structure(users):
    user_names_string = ', '.join(user for user in users)
    string = [str(message_codes["SEND_USERS"]), "#messageText", '["{message}"]'.format(message=user_names_string), "#DONE@"]
    general_message = ''.join(string)
    return general_message

def general_message_structure1(code, msg):
    string = [str(code), "length[", str(len(msg)), "]#messageText", '["{message}"]'.format(message=msg), "#DONE!"]
    general_message = ''.join(string)
    return general_message


"""Create the general_message_structure2- one of the general structures to pass info from client to server (and then p2p)
    :param code: the code of the message, each code means something else
    :param msg: the message that one of the sides wants to send to the other
    :type code: int
    :type msg: string
    :return: a msg to send to the other side
    :rtype: string
    """

def general_message_structure2(code, msg):
    string = ["**", str(code), "#MSG", '["{message}"]'.format(message=msg), "LENGTH[", str(len(msg)), "]#DONE@"]
    general_message = ''.join(string)
    return general_message

"""Create the general_message_structure3- one of the general structures to pass info from client to server (and then p2p)
    :param code: the code of the message, each code means something else
    :param msg: the message that one of the sides wants to send to the other
    :type code: int
    :type msg: string
    :return: a msg to send to the other side
    :rtype: string
    
    HERE- the length is the code, and the length of the actual msg is not here.
    """

def general_message_structure3(code, msg):
    string = [str(code), "#messageText", '["{message}"]'.format(message=msg), "length[", str(len(msg)), "]!DONE@"]
    general_message = ''.join(string)
    return general_message

def extract_message_structure1(general_message):
    start_index = general_message.find('["') + 2
    end_index = general_message.find('"]', start_index)
    return general_message[start_index:end_index]

def extract_message_structure2(general_message):
    start_index = general_message.find('["') + 2
    end_index = general_message.find('"]', start_index)
    return general_message[start_index:end_index]

def extract_message_structure3(general_message):
    start_index = general_message.find('["') + 2
    end_index = general_message.find('"]', start_index)
    return general_message[start_index:end_index]