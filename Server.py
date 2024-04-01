import socket
import Handshake as handshake
import ProtocolStructures as structs
import AES_GCM as aesgcm
import ChaCha20_Poly1305
import threading
import select
import CommandProtocol
import time
import SQLite

class Server:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.PORT = 45000
        self.users = {}
        self.keysAndNonce = {}
        self.lock = threading.Lock()

    def creating_a_listening_sock(self):
        listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.IP, self.PORT)
        listening_sock.bind(server_address)
        listening_sock.listen()  # Adjust the backlog as needed
        print("Server running...")
        timer_thread = threading.Timer(50, self.change_keys)
        timer_thread.start()
        return listening_sock

    def create_connection(self):
        listening_sock = self.creating_a_listening_sock()
        client_sockets = [listening_sock]
        try:
            while True:
                # Use select to wait for any of the sockets to be ready for reading
                ready_to_read, _, _ = select.select(client_sockets, [], [])
                for sock in ready_to_read:
                    if sock == listening_sock:
                        # New client connection
                        client_sock, _ = sock.accept()
                        client_sockets.append(client_sock)
                        threading.Thread(target=self.handle_client, args=(client_sock,)).start()
                    else:
                        # Existing client has sent data
                        threading.Thread(target=self.handle_client_messages, args=(sock,)).start()
        except KeyboardInterrupt:
            print("Server shutting down...")

    def handle_client(self, client_sock):
        with self.lock:
            try:
                msg = self.recv_message(client_sock)
                if "clienthello" in msg:
                    if self.handshake(client_sock, msg) == 2:
                        msg = self.recv_message(client_sock)

                while True:
                    msg = self.recv_message(client_sock)
                    if not msg:
                        return
                    new_msg = self.decryption(msg, self.get_name_by_client_soc(client_sock))
                    if new_msg != b'':
                        print(new_msg)
                        self.get_sender_receiver_and_content(new_msg)

            except socket.timeout:
                print("Socket timed out")
            except Exception as e:
                print(f"Error handling client: {e}")
                # You can handle errors here without removing the client

    def handle_client_messages(self, client_sock):
        with self.lock:
            try:
                msg = self.recv_message(client_sock)
                if not msg:
                    # Client disconnected
                    return
                if msg == b'':
                    return

                new_msg = self.decryption(msg, self.get_name_by_client_soc(client_sock))
                if new_msg != '':
                    self.get_sender_receiver_and_content(new_msg)

            except socket.timeout:
                print("Socket timed out")
            except Exception as e:
                print(f"Error handling client messages: {e}")

    def recv_message(self, client_soc):
        try:
            client_msg = client_soc.recv(1024)
            client_soc.settimeout(3)
            if not client_msg:
                raise Exception("Client disconnected")
            print(client_msg)
            client_msg = client_msg.decode()
            return client_msg
        except Exception as exc:
            return ""

    def change_keys(self):
        for username, user_data in self.users.items():
            print(username)
            client_soc, cryptography, message_template = user_data
            msg, key1, key2 = handshake.update_key_structure(cryptography)
            print(key1)
            print(key2)
            self.send_message(username, msg)
            del self.keysAndNonce[username]
            self.keysAndNonce[username] = [key1.encode('utf-8'), key2.encode('utf-8')]
        timer_thread = threading.Timer(600, self.change_keys)
        timer_thread.start()

    def get_sender_receiver_and_content(self, msg):
        type, sender, receiver, content = CommandProtocol.recv_message(msg)
        if type == "SEND_MESSAGE":
            print(content)
            self.send_to_receiver(sender, receiver, content)
        elif type == "DELETE_MESSAGE":
            self.delete_to_receiver(sender, receiver, content)
        elif type == "EDIT_MESSAGE":
            self.edit_to_receiver(sender, receiver, content)
        elif type == "CHANGE_PASSWORD":
            self.change_password(sender, content)
        elif type == "LOGOUT_MESSAGE":
            print("byebye!")
            self.logout(sender)

    def change_password(self, sender, content):
        db = SQLite.DB()
        db.change_password(sender, content)
    def logout(self, sender):
        del self.users[sender]
        del self.keysAndNonce[sender]
        self.send_users()

    def send_to_receiver(self, sender, receiver, content):
        msg = CommandProtocol.send_message_back(sender, receiver, content)
        print(msg)
        self.send_message(receiver, msg)
    def delete_to_receiver(self, sender, receiver, content):
        msg = CommandProtocol.delete_message(sender, receiver, content)
        self.send_message(receiver, msg)
    def edit_to_receiver(self, sender, receiver, content):
        msg = CommandProtocol.edit_message(sender, receiver, content)
        self.send_message(receiver, msg)

    def send_message(self, name, msg):
        clientsock = None
        for clientname, user_info in self.users.items():
            if name == clientname:
                clientsock = user_info[0]
        data = self.create_encryption(msg.encode('utf-8'), name)
        print("data: ", data)
        clientsock.sendall(data.encode())

    def get_name_by_client_soc(self, client_soc):
        for name, user_info in self.users.items():
            if user_info[0] == client_soc:
                return name

    def handshake(self, client_soc, msg):
        msg, cryptography, name, message_template = handshake.server_hello_structure(msg)
        self.name = name
        self.users[name] = [client_soc, cryptography, message_template]
        client_soc.sendall(msg.encode())
        msg, key, nonce = handshake.server_approval_structure(cryptography)
        self.keysAndNonce[self.name] = [key.encode('utf-8'), nonce.encode('utf-8')]
        client_soc.sendall(msg.encode())
        msg = self.recv_message(client_soc)
        print(msg)
        client_soc.sendall(msg.encode())
        self.send_users()

    def send_users(self):
        message_template = "Users connected: {}"
        connected_users = ', '.join(self.users.keys())
        full_message = message_template.format(connected_users)
        print(full_message)
        for name, client_data in self.users.items():
            self.send_message(name, full_message)

    def use_chacha20_poly1305(self, msg, name):
        crypto = ChaCha20_Poly1305.ChaCha20_Poly1305()
        crypto.set_key(self.keysAndNonce[name][0])
        crypto.set_nonce(self.keysAndNonce[name][1])
        new_msg = crypto.encrypt_or_decrypt(msg)
        return new_msg

    def use_aes_gcm(self, msg, name):
        crypto = aesgcm.AES_GCM()
        crypto.set_key(self.keysAndNonce[name][0])
        crypto.set_iv(self.keysAndNonce[name][1])
        new_msg = crypto.encrypt_or_decrypt(msg)
        return new_msg

    def use_structure_1(self, code, encrypted_msg):
        return structs.general_message_structure1(code, encrypted_msg)

    def use_structure_2(self, code, encrypted_msg):
        return structs.general_message_structure2(code, encrypted_msg)

    def use_structure_3(self, code, encrypted_msg):
        return structs.general_message_structure3(code, encrypted_msg)

    def create_encryption(self, msg, name):
        new_msg = ""
        if self.users[name][1] == "AES GCM":
            new_msg = self.use_aes_gcm(msg, name)
        else:
            new_msg = self.use_chacha20_poly1305(msg, name)
        print("new_msg: ", new_msg)
        if self.users[name][2] == 1:
            return self.use_structure_1(150, new_msg)
        elif self.users[name][2] == 2:
            return self.use_structure_2(150, new_msg)
        else:
            return self.use_structure_3(150, new_msg)

    def decryption(self, msg, name):
        new_msg = ""
        if "#DONE!" in msg:
            new_msg = structs.extract_message_structure1(msg)
        elif "#DONE@" in msg:
            new_msg = structs.extract_message_structure2(msg)
        else:
            new_msg = structs.extract_message_structure3(msg)
        new_msg = eval(new_msg)
        print("new_msg ", new_msg)
        if self.users[name][1] == "AES GCM":
            return self.use_aes_gcm(new_msg, name)
        else:
            return self.use_chacha20_poly1305(new_msg, name)

server = Server()
server.create_connection()