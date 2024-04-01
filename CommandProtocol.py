# Commands Protocol-

def recv_message(msg):
    """Parse a received message and extract sender, receiver, and content
    :param received_message: the received message from the server
    :type received_message: string
    :return: a tuple containing sender, receiver, and content
    :rtype: tuple
    """
    # Split the received message into parts
    if isinstance(msg, bytes):
        msg = msg.decode()
    parts = msg.split()
    type = parts[0]
    sender = parts[1]
    receiver = parts[2]
    content = " ".join(parts[3:])
    return type, sender, receiver, content

def send_message(sender, receiver, content):
    """Send a message from one user to another
    :param sender: the username of the sender
    :param receiver: the username of the message receiver
    :param content: the content of the message
    :type sender: string
    :type receiver: string
    :type content: string
    :return: a message to send to the server to transmit the user's message
    :rtype: string
    """
    message = f"SEND_MESSAGE {sender} {receiver} {content}"
    return message

def send_message_back(sender, receiver, content):
    """Send a message from one user to another
    :param sender: the username of the sender
    :param receiver: the username of the message receiver
    :param content: the content of the message
    :type sender: string
    :type receiver: string
    :type content: string
    :return: a message to send to the server to transmit the user's message
    :rtype: string
    """
    message = f"SEND_MESSAGE_BACK {sender} {receiver} {content}"
    return message

def change_password(username, new_password):
    """Change a user's password
    :param username: the username of the user
    :param new_password: the new password for the user
    :type username: string
    :type new_password: string
    :return: a message to send to the server to change the user's password
    :rtype: string
    """
    message = f"CHANGE_PASSWORD {username} {"none"} {new_password}"
    return message

def delete_message(sender, receiver, content):
    message = f"DELETE_MESSAGE {sender} {receiver} {content}"
    return message

def edit_message(sender, receiver, content):
    message = f"EDIT_MESSAGE {sender} {receiver} {content}"
    return message

def logout(sender):
    message = f"LOGOUT_MESSAGE {sender} {"none"} {"none"}"
    return message