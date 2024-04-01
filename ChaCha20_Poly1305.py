import random

bits_32 = 0xFFFFFFFF#put everything on 32 bits count
bits_64 = 64

class ChaCha20_Poly1305:

    def __init__(self):
        self.key = "none".encode('utf-8')
        self.nonce = ""
        self.counter = 0
        self.random = random.randint(1, 9)

    def set_key(self, key):
        self.key = key

    def set_nonce(self, nonce):
        self.nonce = nonce

    def rotate(self, arr, left):
        return (arr << left)

    def quarter_round(self, a, b, c, d):
        a = (a + b) & bits_32
        d = (d ^ a)
        d = d & bits_32
        d = self.rotate(d, 16)
        c = (c + d) & bits_32
        b = (b ^ c)
        b = b & bits_32
        b = self.rotate(b, 12)
        a = (a + b) & bits_32
        d = (d ^ a)
        d = d & bits_32
        d = self.rotate(d, 8)
        c = (c + d) & bits_32
        b = (b ^ c)
        b = b & bits_32
        b = self.rotate(b, 7)
        return a, b, c, d

    def create_pseudorandom_stream(self, block):
        for i in range(0, 10):
            block[0], block[4], block[8], block[12] = self.quarter_round(block[0], block[4], block[8], block[12])
            block[1], block[5], block[9], block[13] = self.quarter_round(block[1], block[5], block[9], block[13])
            block[2], block[6], block[10], block[14] = self.quarter_round(block[2], block[6], block[10], block[14])
            block[3], block[7], block[11], block[15] = self.quarter_round(block[3], block[7], block[11], block[15])
        return block

    def get_blocks(self):
        result = bytearray(bits_64)
        constants = b'\x03' * 16 + self.key + b'\x03' * 16  # 64 bits needed
        blocks = []
        for i in range(0, bits_64, 4):
            blocks.append(int.from_bytes(constants[i:i + 4]))
        blocks[12] = self.counter
        blocks[13] = int.from_bytes(self.nonce[0:4])
        blocks[14] = int.from_bytes(self.nonce[4:len(self.nonce)])
        block = blocks  # copy, (16 bits)
        block = self.create_pseudorandom_stream(block)
        for i in range(16):
            result[i * 4: (i * 4 + 4)] = ((blocks[i] + block[i]) & bits_32).to_bytes(4)
        return result

    def encrypt_or_decrypt(self, text):
        encrypted_text = b''
        self.counter = 0
        while (len(text) > 0):
            key = self.get_blocks()
            block = text[0:bits_64]
            length_of_data = len(block)
            encrypted_block = bytearray(length_of_data)
            for i in range(length_of_data):
                encrypted_block[i] = (block[i] ^ key[i])
            encrypted_text += encrypted_block
            self.counter += 1
            text = text[bits_64:len(text)]
        return encrypted_text

