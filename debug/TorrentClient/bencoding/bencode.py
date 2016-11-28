'''
Bencoding

Bencoding is a way to specify and organize data in a terse format. It
supports the following types: byte strings, integers, lists, and
dictionaries.

Byte Strings

Byte strings are encoded as follows: <string length encoded in base ten
ASCII>:<string data> Note that there is no constant beginning delimiter,
and no ending delimiter.

    Example: 4: spam represents the string "spam"
    Example: 0: represents the empty string ""

Integers

Integers are encoded as follows: i<integer encoded in base ten ASCII>e
The initial i and trailing e are beginning and ending delimiters.

    Example: i3e represents the integer "3"
    Example: i-3e represents the integer "-3"

i-0e is invalid. All encodings with a leading zero, such as i03e, are
invalid, other than i0e, which of course corresponds to the integer "0".

    NOTE: The maximum number of bit of this integer is unspecified, but
    to handle it as a signed 64bit integer is mandatory to handle "large
    files" aka .torrent for more that 4Gbyte.

Lists

Lists are encoded as follows: l<bencoded values>e
The initial l and trailing e are beginning and ending delimiters. Lists
may contain any bencoded type, including integers, strings,
dictionaries, and even lists within other lists.

    Example: l4:spam4:eggse represents the list of two strings:
    "spam", "eggs" ]
    Example: le represents an empty list:
    []

Dictionaries

Dictionaries are encoded as follows:
d<bencoded string><bencoded element>e
The initial d and trailing e are the beginning and ending delimiters.
Note that the keys must be bencoded strings. The values may be any
bencoded type, including integers, strings, lists, and other
dictionaries.
Keys must be strings and appear in sorted order (sorted as raw strings,
not alphanumerics). The strings should be compared using a binary
comparison, not a culture-specific "natural" comparison.

    Example: d3:cow3:moo4:spam4:eggse represents the dictionary
    { "cow" => "moo", "spam" => "eggs" }
    Example: d4:spaml1:a1:bee represents the dictionary
    { "spam" => [ "a","b" ] }
    Example: de represents an empty dictionary
    {}
'''

import re
import string
import itertools


def encode(data):
    if isinstance(data, int):
        return b"i" + str(data).encode() + b"e"
    elif isinstance(data, bytes):
        return str(len(data)).encode() + b":" + data
    elif isinstance(data, str):
        return encode(data.encode("ascii"))
    elif isinstance(data, list):
        return b"l" + b"".join(map(encode, data)) + b"e"
    elif isinstance(data, dict):
        if all(isinstance(i, bytes) for i in data.keys()):
            items = list(data.items())
            items.sort()
            return b"d" + b"".join(map(encode, itertools.chain(*items))) + b"e"
        else:
            raise ValueError("dict keys should be bytes")
    raise ValueError("Allowed types: int, bytes, list, dict; not %s",
                     type(data))


def decode(s):
    def decode_first(s):
        if s.startswith(b"i"):
            match = re.match(b"i(-?\\d+)e", s)
            return int(match.group(1)), s[match.span()[1]:]
        elif s.startswith(b"l") or s.startswith(b"d"):
            l = []
            rest = s[1:]
            while not rest.startswith(b"e"):
                elem, rest = decode_first(rest)
                l.append(elem)
            rest = rest[1:]
            if s.startswith(b"l"):
                return l, rest
            else:
                return {i: j for i, j in zip(l[::2], l[1::2])}, rest
        elif any(s.startswith(i.encode()) for i in string.digits):
            m = re.match(b"(\\d+):", s)
            length = int(m.group(1))
            rest_i = m.span()[1]
            start = rest_i
            end = rest_i + length
            return s[start:end], s[end:]
        else:
            raise ValueError("Malformed input.")

    if isinstance(s, str):
        s = s.encode("ascii")

    ret, rest = decode_first(s)
    if rest:
        raise ValueError("Malformed input.")
    return ret


if __name__ == "__main__":
    pass
