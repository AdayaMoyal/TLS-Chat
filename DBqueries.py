import sqlite3

def add_user(username, password, email):
    """Add a new user to the 'users' table.
    :param username: the username of the new user
    :param password: the password of the new user
    :param email: the email of the new user #do we need email?
    """
    connection_users = sqlite3.connect('users.db')
    cursor_users = connection_users.cursor()
    cursor_users.execute("""
        INSERT INTO users (username, password, email, phone)
        VALUES (?, ?, ?, ?)
    """, (username, password, email))
    connection_users.commit()
    connection_users.close()

def update_user_password(username, new_password):
    """Update the password of an existing user in the 'users' table.
    :param username: the username of the user
    :param new_password: the new password for the user
    """
    connection_users = sqlite3.connect('users.db')
    cursor_users = connection_users.cursor()
    cursor_users.execute("""
        UPDATE users
        SET password = ?
        WHERE username = ?
    """, (new_password, username))
    connection_users.commit()
    connection_users.close()

def get_user_info(username):
    """Get information about a user from the 'users' table.
    :param username: the username of the user
    :return: a tuple containing user information (userId, username, password, email)
    """
    connection_users = sqlite3.connect('users.db')
    cursor_users = connection_users.cursor()
    cursor_users.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, (username,))
    user_info = cursor_users.fetchone()
    connection_users.close()
    return user_info


def add_message(users, message_sender, message_data):
    """Add a new message to the 'chatsHistory' table.
    :param users: a string representing the users involved in the chat
    :param message_sender: the username of the message sender
    :param message_data: the content of the message
    """
    connection_chats = sqlite3.connect('history.db')
    cursor_chats = connection_chats.cursor()
    cursor_chats.execute("""
        INSERT INTO history (users, messageSender, messageData)
        VALUES (?, ?, ?)
    """, (users, message_sender, message_data))
    connection_chats.commit()
    connection_chats.close()

def get_messages_for_user(username):
    """Get messages for a specific user from the 'chatsHistory' table.
    :param username: the username of the user
    :return: a list of tuples containing message information (messageId, users, messageSender, messageData)
    """
    connection_chats = sqlite3.connect('history.db')
    cursor_chats = connection_chats.cursor()
    cursor_chats.execute("""
        SELECT * FROM history
        WHERE users LIKE ? OR messageSender = ?
    """, ('%' + username + '%', username))
    messages = cursor_chats.fetchall()
    connection_chats.close()
    return messages

