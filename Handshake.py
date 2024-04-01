from string import ascii_lowercase
from string import digits
import random

"""Update the encryption key every 10 minutes
    :param new_key: the new encryption key
    :type new_key: string
    :return: a new structure updated with the new key
    :rtype: string
    """
def update_key_structure(cryptography):
    hashed_key1 = 0
    hashed_key2 = 0
    if cryptography == "AES GCM":
        hashed_key1 = ''.join(random.choices(ascii_lowercase, k=32))
        hashed_key2 = ''.join(random.choices(ascii_lowercase, k=12))
    elif cryptography == "ChaCha20-Poly1305":
        hashed_key1 = ''.join(random.choices(ascii_lowercase, k=32))
        hashed_key2 = ''.join(random.choices(ascii_lowercase, k=8))
    print(hashed_key1)
    print(hashed_key2)
    new_structure = f'UPDATE_KEY {hashed_key1} {hashed_key2}'
    return new_structure, hashed_key1, hashed_key2


"""Create the clienthello- the message the client sends when he wants to start the conversation (part of the handshake)
    :param crypto_packages: the crypto packages the client has (for example, AES GCM)
    :param message_templates: the message templates that the client is willing to talk in
    :param name: name of the client 
    :param options: if there are any other options the client wants to add
    :type crypto_packages: list of strings
    :type message_templates: list of ints
    :type name: string
    :type options: string
    :return: a structure of the clienthello message
    :rtype: string
    """


def client_hello_structure(crypto_packages, message_templates, name, options):
    string = ["clienthello@cryptography["]
    for index, package in enumerate(crypto_packages):
        string.append(str(package))
        if index < len(crypto_packages) - 1:
            string.append(", ")
    string.append("]#messagetemplates[")
    for index, template in enumerate(message_templates):
        string.append(str(template))
        if index < len(message_templates) - 1:
            string.append(", ")
    string.append("]#name[" + '"{name}"'.format(name=name))
    string.append("]#options[" + options + "]==")
    new_structure = ''.join(string)
    return new_structure


"""Create the serverhello- the message the server sends when to the client (part of the handshake)
    :param crypto_package: the crypto packages the server decided to use
    :param message_template: the message template the client server decide to use
    :param options: if there are any other options the server wants to add
    :type crypto_package: string
    :type message_template: int
    :type options: string
    :return: a structure of the serverhello message
    :rtype: string
    """


def server_hello_structure(msg):
    crypto_packages, message_templates, name, options = clients_info(msg)
    crypto_package = random.choice(crypto_packages)
    message_template = random.choice(message_templates)
    string = ["serverhello@cryptography[", crypto_package, "]#messagetemplates[", str(message_template), "]#options[",
              options, "]=="]
    new_structure = ''.join(string)
    return new_structure, crypto_package, name, message_template


def clients_info(msg):
    crypto_start = msg.find("clienthello@cryptography[") + len("clienthello@cryptography[")
    crypto_end = msg.find("]#messagetemplates[")
    templates_start = crypto_end + len("]#messagetemplates[")
    templates_end = msg.find("]#name[")
    crypto_packages = msg[crypto_start:crypto_end].split(", ")  # create the list
    message_templates = msg[templates_start:templates_end].split(", ")  # create the list
    name_start = templates_end + len("]#name[")
    name_end = msg.find("]#options[")
    options_start = name_end + len("]#options[")
    options_end = msg.find("]==")
    name = msg[name_start:name_end].strip('""')  # remove the ""
    options = msg[options_start:options_end]
    return crypto_packages, message_templates, name, options


"""Create the serverhellodone- the message the server sends to client in which he approves the clienthello and serverhello
    :param hashed_key: key exchange between server and client
    :type hashed_key: int
    :return: a structure of the serverhellodone message
    :rtype: string
    """


def server_approval_structure(cryptography):
    hashed_key1 = 0
    hashed_key2 = 0
    if cryptography == "AES GCM":
        hashed_key1 = ''.join(random.choices(ascii_lowercase, k=32))
        hashed_key2 = ''.join(random.choices(ascii_lowercase, k=12))
    elif cryptography == "ChaCha20-Poly1305":
        hashed_key1 = ''.join(random.choices(ascii_lowercase, k=32))
        hashed_key2 = ''.join(random.choices(ascii_lowercase, k=8))
    string = ["serverapproval@key[", str(hashed_key1), ", ", str(hashed_key2),
              "]#messageencrypt[yes]#ServerHelloDone=="]
    new_structure = ''.join(string)
    return new_structure, hashed_key1, hashed_key2


"""Create new encryption key
    :param cryptography: the cryptography that is being used
    :type cryptography: string
    :return: a new cryptography key
    :rtype: string
    """
def create_encryption_key(cryptography):
    hashed_key1 = 0
    hashed_key2 = 0
    if cryptography == "AES GCM":
        hashed_key1 = ''.join(random.choices(ascii_lowercase + digits, k=32))
        hashed_key2 = ''.join(random.choices(ascii_lowercase + digits, k=12))
    elif cryptography == "ChaCha20-Poly1305":
        hashed_key1 = ''.join(random.choices(ascii_lowercase + digits, k=32))
        hashed_key2 = ''.join(random.choices(ascii_lowercase + digits, k=8))
    return hashed_key1, hashed_key2


def finished_structure():
    string = ["finished=="]
    new_structure = ''.join(string)
    return new_structure
