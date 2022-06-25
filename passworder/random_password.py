import string
import random

CHARS_ALL = "chars_all"
CHARS_LETTERS = "chars_letters"
CHARS_LOWERCASE = "chars_lower"
CHARS_LOWERCASEDIGITS = "chars_lowerdigits"
collections = {
    CHARS_ALL: string.ascii_letters + string.digits + string.punctuation,
    CHARS_LETTERS: string.ascii_letters,
    CHARS_LOWERCASE: string.ascii_lowercase,
    CHARS_LOWERCASEDIGITS: string.ascii_lowercase + string.digits
}
DEFAULT_LENGTH = 12


def get_random_password(length=DEFAULT_LENGTH, chars=CHARS_LETTERS, seed=None):
    if seed is None:
        random_generator = random.SystemRandom()
    else:
        random_generator = random.Random(seed)
    return "".join(random_generator.choice(chars) for character in range(length))


def get_random_salt(length=8):
    return get_random_password(length=length, chars=CHARS_LETTERS)
