import socket
import Handshake as handshake
import AES_GCM as aesgcm
import ChaCha20_Poly1305
import ProtocolStructures as structs
import Protection_From_Attacks as protection
import CommandProtocol
import select
import SQLite

class Client:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.PORT = 45000
        self.cryptography = ""
        self.key = "none".encode('utf-8')
        self.nonce_or_iv = "none".encode('utf-8')
        self.structure = 0
        self.created = False
        self.socket_created = False
        self.name = ""
        self.password = ""
        self.sock = None
        self.db = SQLite.DB()

    def creating_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.IP, self.PORT)
        sock.connect(server_address)  # connecting
        self.socket_created = True
        self.sock = sock
        return sock

    def login(self, name, password):
        self.name = name
        self.password = password

    def recv_message(self, sock):
        try:
            server_msg = sock.recv(1024)
            server_msg = server_msg.decode()
            return server_msg
        except Exception as exc:
            pass

    def connect_to_server(self):
        while 1:
            if not self.socket_created:
                try:
                    sock = self.creating_sock()
                except Exception as exc:  # when the server crashes
                    print("The server crashed.")
                    break
            try:
                if not self.created:
                    self.handshake(sock)
            except Exception as exc:
                print(exc) # prints nothing - In order not to interfere with the conversation

    def send_message_to_friend(self, text, friends_name, sender):
        #if protection.check_for_sql_injection(msg) or protection.check_length_of_msg(msg):
        #    msg = "This message does not meet the terms of the software, so it will not be sent."
        msg = CommandProtocol.send_message(sender, friends_name, text)
        self.send_message(msg, self.sock)

    def send_message_to_socket(self, msg):
        self.send_message(msg, self.sock)

    def recv_message_from_friend(self, msg):
        #if protection.check_for_sql_injection(msg) or protection.check_length_of_msg(msg):
        #    msg = "This message does not meet the terms of the software, so it will not be sent."
        msg = self.decryption(msg)
        type, sender, friends_name, data = CommandProtocol.recv_message(msg)
        return sender, friends_name, data

    def handshake(self, sock):
        self.created = True
        msg = handshake.client_hello_structure(["AES GCM", "ChaCha20-Poly1305"], [1, 2, 3], self.name, "None")
        sock.sendall(msg.encode())
        msg = self.recv_message(sock)
        self.check_cryptography_and_structure(msg)
        print(msg)
        msg = self.recv_message(sock)
        self.get_key_nonce_iv(msg)
        print(msg)
        msg = handshake.finished_structure()
        sock.sendall(msg.encode())
        msg = self.recv_message(sock)
        print(msg)

    def check_cryptography_and_structure(self, msg):
        if "AES GCM" in msg:
            self.cryptography = "AES GCM"
        elif "ChaCha20-Poly1305" in msg:
            self.cryptography = "ChaCha20-Poly1305"
        crypto_struct = msg.split("#")
        if "1" in crypto_struct[1]:
            self.structure = 1
        elif "2" in crypto_struct[1]:
            self.structure = 2
        else:
            self.structure = 3

    def get_key_nonce_iv(self, msg):
        crypto_start = msg.find("serverapproval@key[") + len("serverapproval@key[")
        crypto_end = msg.find("]#messageencrypt[yes]#ServerHelloDone==")
        crypto_keys = msg[crypto_start:crypto_end].split(", ")
        self.key = crypto_keys[0].encode('utf-8')
        self.nonce_or_iv = crypto_keys[1].encode('utf-8')

    def use_chacha20_poly1305(self, msg):
        crypto = ChaCha20_Poly1305.ChaCha20_Poly1305()
        crypto.set_key(self.key)
        crypto.set_nonce(self.nonce_or_iv)
        new_msg = crypto.encrypt_or_decrypt(msg)
        return new_msg

    def use_aes_gcm(self, msg):
        crypto = aesgcm.AES_GCM()
        crypto.set_key(self.key)
        crypto.set_iv(self.nonce_or_iv)
        new_msg = crypto.encrypt_or_decrypt(msg)
        return new_msg

    def use_structure_1(self, code, encrypted_msg):
        return structs.general_message_structure1(code, encrypted_msg)

    def use_structure_2(self, code, encrypted_msg):
        return structs.general_message_structure2(code, encrypted_msg)

    def use_structure_3(self, code, encrypted_msg):
        return structs.general_message_structure3(code, encrypted_msg)

    def create_encryption(self, msg):
        new_msg = ""
        code = 0
        if self.cryptography == "AES GCM":
            code = 206
            if "SEND_MESSAGE" in msg.decode():
                code = 205
            new_msg = self.use_aes_gcm(msg)  # Encode the original message
        else:
            code = 204
            if "SEND_MESSAGE" in msg.decode():
                code = 207
            new_msg = self.use_chacha20_poly1305(msg)  # Encode the original message
        if self.structure == 1:
            return self.use_structure_1(code, new_msg)
        elif self.structure == 2:
            return self.use_structure_2(code, new_msg)
        else:
            return self.use_structure_3(code, new_msg)

    def decryption(self, msg):
        new_msg = ""
        if self.structure == 1:
            new_msg = structs.extract_message_structure1(msg)
        elif self.structure == 2:
            new_msg = structs.extract_message_structure2(msg)
        else:
            new_msg = structs.extract_message_structure3(msg)
        new_msg = eval(new_msg)
        print(new_msg)
        if self.cryptography == "AES GCM":
            return self.use_aes_gcm(new_msg)  # Decode the decrypted bytes to string
        else:
            return self.use_chacha20_poly1305(new_msg)

    def send_message(self, msg, sock):
        data = self.create_encryption(msg.encode('utf-8'))
        sock.sendall(data.encode())

