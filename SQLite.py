import sqlite3
import threading
from datetime import datetime

class DB:
    def __init__(self):
        self.lock_users = threading.Lock()
        self.lock_chats = threading.Lock()
        self.lock = threading.Lock()
        self.connection_users = None
        self.connection_chats = None
        self.connect_users_db()
        self.connect_chats_history_db()

    def connect_users_db(self):
        with self.lock_users:
            self.connection_users = sqlite3.connect('db/users.db', check_same_thread=False)
            self.create_users_db()

    def connect_chats_history_db(self):
        with self.lock_chats:
            self.connection_chats = sqlite3.connect('db/history.db', check_same_thread=False)
            self.create_chats_history_db()

    def close_connections(self):
        if self.connection_users:
            self.connection_users.close()
        if self.connection_chats:
            self.connection_chats.close()

    def create_users_db(self):
        cursor_users = self.connection_users.cursor()
        cursor_users.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                    userId INTEGER PRIMARY KEY,
                    username TEXT NOT NULL CHECK(length(username) <= 16),
                    password TEXT NOT NULL CHECK(length(password) >= 8),
                    email TEXT,
                    phone TEXT)""")

    def create_chats_history_db(self):
        cursor_chats = self.connection_chats.cursor()
        cursor_chats.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                    users TEXT,
                    messageSender TEXT,
                    messageReceiver TEXT,
                    messageId INTEGER,
                    messageTime TEXT,
                    messageData TEXT)""")

    def add_a_user(self, username, password, email, phone):
        try:
            id = self.get_last_user_id()
            user_info = (id + 1, username, password, email, phone)
            sql = '''INSERT INTO users(userId, username, password, email, phone)
                              VALUES(?,?,?,?,?)'''
            cur = self.connection_users.cursor()
            cur.execute(sql, user_info)
            self.connection_users.commit()
        except Exception as e:
            return 2

    def user_exists(self, username, password):
        with self.lock_users:
            cursor_users = self.connection_users.cursor()
            cursor_users.execute("SELECT COUNT(*) FROM users WHERE username=? AND password=?", (username, password))
            user_count = cursor_users.fetchone()[0]
            return user_count > 0

    def add_chats_history(self, messageSender, messageReceiver, messageData):
        users = '&'.join(sorted([messageSender, messageReceiver]))
        current_time = datetime.now()
        formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
        with self.lock_chats:
            last_id = self.get_last_message_id(messageSender, messageReceiver)
            sql = '''INSERT INTO history(users, messageSender, messageReceiver, messageId, messageTime, messageData)
                          VALUES(?,?,?,?,?,?)'''
            history = (users, messageSender, messageReceiver, last_id + 1, formatted_time, messageData)
            cur = self.connection_chats.cursor()
            cur.execute(sql, history)
            self.connection_chats.commit()
        return formatted_time

    def get_last_user_id(self):
        with self.lock_users:
            cursor_users = self.connection_users.cursor()
            cursor_users.execute("SELECT MAX(userId) FROM users")
            result = cursor_users.fetchone()
            if result[0] is None:
                return 0
            return result[0]

    def get_last_message_id(self, sender, receiver):
        users = '&'.join(sorted([sender, receiver]))
        cursor_chats = self.connection_chats.cursor()
        cursor_chats.execute("SELECT MAX(messageId) FROM history WHERE users=?",
                             (users,))
        result = cursor_chats.fetchone()
        if result is None or result[0] is None:
            return 0
        return result[0]
    def get_message_id_based_on_info(self, sender, receiver, time):
        users = '&'.join(sorted([sender, receiver]))
        cursor_chats = self.connection_chats.cursor()
        sql_request = '''SELECT MAX(messageId) FROM history WHERE users=? AND messageSender=? AND messageReceiver=? AND messageTime=?'''
        cursor_chats.execute(sql_request, (users, sender, receiver, time))
        result = cursor_chats.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_messages(self, sender, receiver):
        users = '&'.join(sorted([sender, receiver]))
        cursor_chats = self.connection_chats.cursor()
        cursor_chats.execute("SELECT * FROM history WHERE users=?", (users,))
        messages = cursor_chats.fetchall()
        return messages

    def return_all_users(self):
        with self.lock_users:
            cursor_users = self.connection_users.cursor()
            cursor_users.execute("SELECT username FROM users")
            usernames = [row[0] for row in cursor_users.fetchall()]
            return usernames

    def edit_message(self, sender, receiver, time, new_message):
        message_id = self.get_message_id_based_on_info(sender, receiver, time)
        users = '&'.join(sorted([sender, receiver]))
        cursor_chats = self.connection_chats.cursor()
        sql_request = '''UPDATE history SET messageData=? WHERE users=? AND messageSender=? AND messageReceiver=? AND messageId=? AND messageTime=?'''
        cursor_chats.execute(sql_request, (new_message, users, sender, receiver, message_id, time))
        self.connection_chats.commit()

    def delete_message(self, sender, receiver, time):
        message_id = self.get_message_id_based_on_info(sender, receiver, time)
        users = '&'.join(sorted([sender, receiver]))
        cursor_chats = self.connection_chats.cursor()
        sql_request = '''DELETE FROM history WHERE users=? AND messageSender=? AND messageReceiver=? AND messageId=? AND messageTime=?'''
        cursor_chats.execute(sql_request, (users, sender, receiver, message_id, time))
        self.connection_chats.commit()

    def change_password(self, user, new_password):
        cursor_users = self.connection_users.cursor()
        cursor_users.execute("""UPDATE users SET password = ? WHERE username = ?"""
                             ,(new_password, user))
        self.connection_users.commit()