import random
import crypto_utils
from abc import ABC, abstractmethod


def ascii_value(character):
    return ord(character) - 32


def from_ascii_value(value):
    return chr(value + 32)


class Cipher(ABC):
    @staticmethod
    @abstractmethod
    def encode(key, clear_text):
        pass

    @staticmethod
    @abstractmethod
    def decode(key, encoded_text):
        pass

    @classmethod
    def verify(cls, encoding_key, decoding_key, clear_text):
        encoded = cls.encode(encoding_key, clear_text)
        decoded = cls.decode(decoding_key, encoded)
        assert clear_text == decoded

    @staticmethod
    @abstractmethod
    def gen_key_pair(encoding_key=None):
        """Generate a key pair, where first is for encoding and second is for decoding."""
        pass


class Caesar(Cipher):
    @staticmethod
    def encode(key, clear_text):
        result = ''
        for c in clear_text:
            result += from_ascii_value((ascii_value(c) + key) % 95)
        return result

    @classmethod
    def decode(cls, key, encoded_text):
        # Encoding and decoding is the same, but with differing keys
        return cls.encode(key, encoded_text)

    @staticmethod
    def gen_key_pair(encoding_key=None):
        if encoding_key is None:
            encoding_key = random.randint(1, 94)
        return (encoding_key, 95 - encoding_key)


class Multiplicative(Cipher):
    @staticmethod
    def encode(key, clear_text):
        result = ''
        for c in clear_text:
            result += from_ascii_value((ascii_value(c) * key) % 95)
        return result

    @classmethod
    def decode(cls, key, encoded_text):
        # Encoding and decoding is the same, but with differing keys
        return cls.encode(key, encoded_text)

    @staticmethod
    def gen_key_pair(encoding_key=None):
        if encoding_key is None:
            encoding_key = random.randint(2, 94)
        key_inverse = crypto_utils.modular_inverse(encoding_key, 95)
        return (encoding_key, key_inverse)


class Affine(Cipher):
    @staticmethod
    def encode(key, clear_text):
        return Caesar.encode(key[1], Multiplicative.encode(key[0], clear_text))
    
    @staticmethod
    def decode(key, encoded_text):
        return Multiplicative.decode(key[0], Caesar.decode(key[1], encoded_text))

    @staticmethod
    def gen_key_pair(encoding_key=None):
        if encoding_key is None:
            mult_keys = Multiplicative.gen_key_pair()
            caesar_keys = Caesar.gen_key_pair()
            return ((mult_keys[0], caesar_keys[0]), (mult_keys[1], caesar_keys[1]))

        decode_key = (crypto_utils.modular_inverse(
            encoding_key[0], 95), 95 - encoding_key[1])
        return (encoding_key, decode_key)


class Person:
    key = None
    cipher = None

    def get_key(self):
        return self.key

    def set_key(self, key):
        self.key = key

    def operate_chipher(self, text):
        raise NotImplementedError


class Sender(Person):
    def __init__(self, cipher, key=None):
        self.cipher = cipher
        self.key = key

    def operate_chipher(self, clear_text):
        return self.cipher.encode(self.key, clear_text)


class Receiver(Person):
    def __init__(self, cipher, key=None):
        self.cipher = cipher
        self.key = key

    def operate_chipher(self, encoded_text):
        return self.cipher.decode(self.key, encoded_text)


def main():
    """The main method."""

    (enc_key, dec_key) = Affine.gen_key_pair((3, 2))
    Affine.verify(enc_key, dec_key, "yeet skeet")


if __name__ == "__main__":
    main()
