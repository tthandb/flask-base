import random
import string


def random_string_digits(string_length=6):
    """Generate a random string of letters and digits """
    characters = string.ascii_letters + string.digits
    return ''.join(
        random.choice(characters) for i in range(string_length)
    )
