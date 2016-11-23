import random
from string import ascii_letters, digits


def generate_peer_id():
    """ Returns a 20-byte peer id. """
    CLIENT_ID = "ST"
    CLIENT_VERSION = "0001"
    ALPHANUM = ascii_letters + digits
    random_string = ''.join(random.sample(ALPHANUM, 13))
    return "-" + CLIENT_ID + CLIENT_VERSION + random_string
