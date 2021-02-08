"""Main"""

import random
import io
from abc import ABC, abstractmethod
from itertools import cycle
import crypto_utils


def ascii_value(character):
    """Return the printable ASCII value of the given character."""
    return ord(character) - 32


def from_ascii_value(value):
    """Return the ASCII character corresponding to the given value."""
    return chr(value + 32)


def strict_modular_inverse(int_a, int_m):
    """Return the modular inverse such that x * a = 1 (mod m), or None if no inverse exists."""

    gcd, int_x, _ = crypto_utils.extended_gcd(int_a, int_m)
    if gcd != 1:
        return None
    return int_x % int_m


class Cipher(ABC):
    """Abstract Cipher."""

    @staticmethod
    @abstractmethod
    def encode(key, clear_text):
        """Encode the clear text and return it."""

    @staticmethod
    @abstractmethod
    def decode(key, encoded_text):
        """Decode the encoded text and return it."""

    @classmethod
    def verify(cls, encoding_key, decoding_key, clear_text):
        """Run the given clear text through encoding and decoding,verifying that the output remains
        the same."""
        encoded = cls.encode(encoding_key, clear_text)
        decoded = cls.decode(decoding_key, encoded)
        assert clear_text == decoded

    @staticmethod
    @abstractmethod
    def gen_key_pair():
        """Generate a key pair, where the first is for encoding and second is for decoding."""


class Caesar(Cipher):
    """The Caesar cipher."""

    @staticmethod
    def encode(key, clear_text):
        result = ''
        for char in clear_text:
            result += from_ascii_value((ascii_value(char) + key) % 95)
        return result

    @classmethod
    def decode(cls, key, encoded_text):
        # Encoding and decoding is the same, but with differing keys
        return cls.encode(key, encoded_text)

    @classmethod
    def gen_key_pair(cls):
        encoding_key = random.randint(1, 94)
        return (encoding_key, cls.gen_decoding_key(encoding_key))

    @staticmethod
    def gen_decoding_key(encoding_key):
        """Generate a decoding key from the given encoding key."""
        return (95 - encoding_key) % 95


class Multiplicative(Cipher):
    """The Multiplicative cipher."""

    @staticmethod
    def encode(key, clear_text):
        result = ''
        for char in clear_text:
            result += from_ascii_value((ascii_value(char) * key) % 95)
        return result

    @classmethod
    def decode(cls, key, encoded_text):
        # Encoding and decoding is the same, but with differing keys
        return cls.encode(key, encoded_text)

    @classmethod
    def gen_key_pair(cls):
        encoding_key = 0
        decoding_key = None
        while decoding_key is None:
            encoding_key = random.randint(2, 94)
            decoding_key = cls.gen_decoding_key(encoding_key)

        return (encoding_key, decoding_key)

    @staticmethod
    def gen_decoding_key(encoding_key):
        """Generate a decoding key from the given encoding key."""
        return strict_modular_inverse(encoding_key, 95)


class Affine(Cipher):
    """The Affine cipher."""

    @staticmethod
    def encode(key, clear_text):
        return Caesar.encode(key[1], Multiplicative.encode(key[0], clear_text))

    @staticmethod
    def decode(key, encoded_text):
        return Multiplicative.decode(key[0], Caesar.decode(key[1], encoded_text))

    @staticmethod
    def gen_key_pair():
        mult_keys = Multiplicative.gen_key_pair()
        caesar_keys = Caesar.gen_key_pair()
        return ((mult_keys[0], caesar_keys[0]), (mult_keys[1], caesar_keys[1]))

    @staticmethod
    def gen_decoding_key(encoding_key):
        """Generate a decoding key from the given encoding key."""
        return (Multiplicative.gen_decoding_key(encoding_key[0]),
                Caesar.gen_decoding_key(encoding_key[1]))


class Unbreakable(Cipher):
    """The Unbreakable cipher."""

    @staticmethod
    def encode(key, clear_text):
        result = ''
        for (char, key_char) in zip(clear_text, cycle(key)):
            result += from_ascii_value((ascii_value(char) +
                                        ascii_value(key_char)) % 95)
        return result

    @classmethod
    def decode(cls, key, encoded_text):
        return cls.encode(key, encoded_text)

    @classmethod
    def gen_key_pair(cls):
        with open('english_words.txt') as a_file:
            line = next(a_file)
            for num, a_line in enumerate(a_file, 2):
                if random.randrange(num):
                    continue
                line = a_line

        encoding_key = line
        decoding_key = cls.gen_decoding_key(encoding_key)

        return (encoding_key, decoding_key)

    @staticmethod
    def gen_decoding_key(encoding_key):
        """Generate a decoding key from the given encoding key."""
        decoding_key = ''
        for char in encoding_key:
            decoding_key += from_ascii_value((95 - ascii_value(char)) % 95)
        return decoding_key


class RSA(Cipher):
    """The RSA cipher."""

    @staticmethod
    def encode(key, clear_text):
        return [pow(t, key[1], key[0]) for t in crypto_utils.blocks_from_text(clear_text, 1)]

    @staticmethod
    def decode(key, encoded_text):
        return crypto_utils.text_from_blocks([pow(c, key[1], key[0]) for c in encoded_text], 8)

    @staticmethod
    def gen_key_pair():
        prime_p = 0
        prime_q = prime_p
        while prime_p == prime_q:
            prime_p = crypto_utils.generate_random_prime(8)
            prime_q = crypto_utils.generate_random_prime(8)

        num = prime_p * prime_q
        phi = (prime_p - 1) * (prime_q - 1)

        inverse_d = None
        while inverse_d is None:
            rand_e = random.randint(3, phi - 1)
            inverse_d = strict_modular_inverse(rand_e, phi)

        return ((num, rand_e), (num, inverse_d))


class Person(ABC):
    """An abstract Person class."""

    key = None
    cipher = None

    def get_key(self):
        """Get the person's key."""
        return self.key

    def set_key(self, key):
        """Set the person's key."""
        self.key = key

    @abstractmethod
    def operate_chipher(self, text):
        """Use the cipher to encode or decode."""


class Sender(Person):
    """The Sender which encodes a message."""

    def __init__(self, cipher, key):
        self.cipher = cipher
        self.key = key

    def operate_chipher(self, text):
        return self.cipher.encode(self.key, text)


class Receiver(Person):
    """The Receiver which decodes a message."""

    def __init__(self, cipher, key):
        self.cipher = cipher
        self.key = key

    def operate_chipher(self, text):
        return self.cipher.decode(self.key, text)


class Hacker(Person):
    """The Hacker which tries to brute force decode some encoded text.

    Hacker is only able to crack messages consisting of English words, separated by spaces."""

    def __init__(self, cipher):
        self.cipher = cipher

        with open('english_words.txt') as a_file:
            self.english_words = a_file.read()

    def check_correctness(self, text):
        """Check whether the given text consists of English words."""

        for word in text.split(' '):
            word += '\n'
            if not word in self.english_words:
                return False

        return True

    def operate_chipher(self, text):
        if self.cipher is Caesar:
            for key in range(0, 95):
                print('Testing Caesar with decoding key = %d' % key)

                decoded_text = Caesar.decode(key, text)
                if self.check_correctness(decoded_text):
                    return decoded_text

        elif self.cipher is Multiplicative:
            for num in range(1, 95):
                key = strict_modular_inverse(num, 95)
                if key is None:
                    continue

                print('Testing Multiplicative with decoding key = %d' % key)

                decoded_text = Multiplicative.decode(key, text)
                if self.check_correctness(decoded_text):
                    return decoded_text

        elif self.cipher is Affine:
            for i in range(0, 95):
                inverse = strict_modular_inverse(i, 95)
                if inverse is None:
                    continue
                print('Testing Affine with Multiplicative decoding key = %d' % inverse)

                for j in range(0, 95):
                    key = (inverse, j)
                    decoded_text = Affine.decode(key, text)
                    if self.check_correctness(decoded_text):
                        return decoded_text
                print('No matching Caesar decoding key found')

        elif self.cipher is Unbreakable:
            for key in io.StringIO(self.english_words):
                # Remove the newline
                key = key[:-1]
                decode_key = Unbreakable.gen_decoding_key(key)

                print('Testing Unbreakable with encoding key = %s, and decoding key = %s' % (
                    key, decode_key))

                decoded_text = Unbreakable.decode(decode_key, text)
                if self.check_correctness(decoded_text):
                    return decoded_text

        return None


def test_send_receive(cipher, message):
    """Tests and prints the sending and receiving procedure."""

    (enc_key, dec_key) = cipher.gen_key_pair()
    sender = Sender(cipher, enc_key)
    receiver = Receiver(cipher, dec_key)
    print(message)
    print(sent := sender.operate_chipher(message))
    print(receiver.operate_chipher(sent))


def test_hacker(cipher, message, key=None):
    """Tests a Hacker trying to crack an encoded message."""

    if key is None:
        (key, _) = cipher.gen_key_pair()
    encoded_text = cipher.encode(key, message)
    hacker = Hacker(cipher)
    result = hacker.operate_chipher(encoded_text)

    if result is not None:
        print('Managed to crack message: %s' % result)
    else:
        print('Was not able to crack message')


def main():
    """The main method."""
    test_hacker(Unbreakable, "potato tomato", "acrylic")


if __name__ == "__main__":
    main()
