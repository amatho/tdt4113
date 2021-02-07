import random


def ascii_value(character):
    return ord(character) - 32


def from_ascii_value(value):
    return chr(value + 32)


class Cipher:
    @staticmethod
    def encode(key, clear_text):
        raise NotImplementedError

    @staticmethod
    def decode(key, encoded_text):
        raise NotImplementedError

    @classmethod
    def verify(cls, encoding_key, decoding_key, clear_text):
        encoded = cls.encode(encoding_key, clear_text)
        decoded = cls.decode(decoding_key, encoded)
        assert clear_text == decoded

    @staticmethod
    def gen_key_pair():
        """Generate a key pair, where first is for encoding and second is for decoding."""
        raise NotImplementedError


class Caesar(Cipher):
    @staticmethod
    def encode(key, clear_text):
        result = ''
        for c in clear_text:
            result += from_ascii_value((ascii_value(c) + key) % 95)
        return result

    @staticmethod
    def decode(key, encoded_text):
        result = ''
        for c in encoded_text:
            result += from_ascii_value((ascii_value(c) + key) % 95)
        return result

    @staticmethod
    def gen_key_pair():
        key = random.randint(0, 94)
        return (key, 95 - key)


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

    (enc_key, dec_key) = Caesar.gen_key_pair()
    Caesar.verify(enc_key, dec_key, "yeet skeet")


if __name__ == "__main__":
    main()
