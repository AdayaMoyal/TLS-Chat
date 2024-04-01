
# const used in gHash
ghash_const = bytes.fromhex("00000000000000000000000000000087")

NULL = b'\x00'
POLYNOMIAL = bytes([0x1, 0x1, 0xb])
DECRYPT = 1
TO_THE_LEFT = 7
TO_THE_RIGHT = 7
BITS = 16

# '|' - OR operation
# '&' - AND operation

class AES_GCM:
    def __init__(self):
        self.key = bytearray(BITS*2)
        self.initializationVector = bytearray(12)

    def set_key(self, key):
        self.key = bytearray(key)

    def set_iv(self, iv):
        self.initializationVector = bytearray(iv)

    def xor_between_2_arrays(self, first, second):
        return(bytes(a ^ b for (a, b) in zip(first, second)))

        # perform xor between the key and the current block
    def gHash(self, key, info):
        tag = bytearray(key)
        for i in range(0, len(info), BITS):
            block = info[i:i + BITS]
            tag = self.xor_between_2_arrays(tag, block)
            tag = self.multiply_in_gf_2_128(tag, ghash_const)
        return tag

    # Shifts a byte array to the left
    def shift_to_the_left(self, array):
        carry = 0
        length_of_array = len(array)
        changed = bytearray(length_of_array)
        for i in range(0, length_of_array):
            updated_carry = (array[i] & 0x80)
            updated_carry = updated_carry >> TO_THE_LEFT
            changed[i] = ((array[i] << 1) | carry) & 0xFF
            carry = updated_carry
        return changed

    # Shifts a byte array to the right
    def shift_to_the_right(self, array):
        carry = 0
        length_of_array = len(array)
        changed = bytearray(length_of_array)
        for i in reversed(range(length_of_array)):
            changed[i] = ((array[i] >> 1) | carry) & 0xFF
            if i != 0:
                carry = (array[i] & 1)
                carry = carry << TO_THE_RIGHT
            else:
                carry = 0
        return changed

    def multiply_in_gf_2_128(self, a, b):#version (2^128)
        result = bytearray(BITS)
        for i in range(0, 128):
            byte_1 = b[len(b) - 1]
            byte_2 = a[len(a) - 1]
            if byte_1 & 1:
                result = self.xor_between_2_arrays(result, a)
            if byte_2 & 0:
                a = self.xor_between_2_arrays(a, POLYNOMIAL)
            a = self.shift_to_the_left(a)
            b = self.shift_to_the_right(b)
        return result

    def increase_counter_by_1(self, counter):
        length = len(counter)
        number = (int.from_bytes(counter, 'little')) + 1
        return number.to_bytes(length, 'little')

    ###Steps Of Encryption Or Decryption:
        #1. Get each block by order
        #2. Increment the counter for each block
        #3. Encrypt/Decrypt the counter using gHash
        #4. Update the ciphertext
    def encrypt_or_decrypt(self, text):
        ciphertext = b''
        counter = self.initializationVector + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
        key = self.gHash(bytearray(BITS), self.key)
        for i in range(0, len(text), 12):
            block = text[i:i+12]
            counter = self.increase_counter_by_1(counter)
            encrypted_counter = self.gHash(key, counter)
            ciphertext += self.xor_between_2_arrays(block, encrypted_counter)
        return ciphertext
