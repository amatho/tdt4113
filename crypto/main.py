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
    def gen_key_pair(key=None):
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
    def gen_key_pair(key=None):
        if key is None:
            key = random.randint(1, 94)
        return (key, 95 - key)


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
    def gen_key_pair(key=None):
        if key is None:
            key = random.randint(2, 94)
        key_inverse = crypto_utils.modular_inverse(key, 95)
        return (key, key_inverse)


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

    (enc_key, dec_key) = Multiplicative.gen_key_pair(3)
    Multiplicative.verify(enc_key, dec_key, "yeet skeet")


if __name__ == "__main__":
    main()
