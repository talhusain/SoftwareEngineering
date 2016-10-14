'''
Bencoding

Bencoding is a way to specify and organize data in a terse format. It supports the following types: byte strings, integers, lists, and dictionaries.

Byte Strings

Byte strings are encoded as follows: <string length encoded in base ten ASCII>:<string data>
Note that there is no constant beginning delimiter, and no ending delimiter.

    Example: 4: spam represents the string "spam"
    Example: 0: represents the empty string ""

Integers

Integers are encoded as follows: i<integer encoded in base ten ASCII>e
The initial i and trailing e are beginning and ending delimiters.

    Example: i3e represents the integer "3"
    Example: i-3e represents the integer "-3"

i-0e is invalid. All encodings with a leading zero, such as i03e, are invalid, other than i0e, which of course corresponds to the integer "0".

    NOTE: The maximum number of bit of this integer is unspecified, but to handle it as a signed 64bit integer is mandatory to handle "large files" aka .torrent for more that 4Gbyte.

Lists

Lists are encoded as follows: l<bencoded values>e
The initial l and trailing e are beginning and ending delimiters. Lists may contain any bencoded type, including integers, strings, dictionaries, and even lists within other lists.

    Example: l4:spam4:eggse represents the list of two strings: [ "spam", "eggs" ]
    Example: le represents an empty list: []

Dictionaries

Dictionaries are encoded as follows: d<bencoded string><bencoded element>e
The initial d and trailing e are the beginning and ending delimiters. Note that the keys must be bencoded strings. The values may be any bencoded type, including integers, strings, lists, and other dictionaries.
Keys must be strings and appear in sorted order (sorted as raw strings, not alphanumerics). The strings should be compared using a binary comparison, not a culture-specific "natural" comparison.

    Example: d3:cow3:moo4:spam4:eggse represents the dictionary { "cow" => "moo", "spam" => "eggs" }
    Example: d4:spaml1:a1:bee represents the dictionary { "spam" => [ "a", "b" ] }
    Example: d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee represents { "publisher" => "bob", "publisher-webpage" => "www.example.com", "publisher.location" => "home" }
    Example: de represents an empty dictionary {}
'''

import itertools

class Bencode(object):
    '''
    All strings are expected to be byte strings. ie: b'test' not 'test'
    '''
    def encode(data):
        if isinstance(data, int):
            return b"i" + str(data).encode() + b"e"
        elif isinstance(data, bytes):
            return str(len(data)).encode() + b":" + data
        elif isinstance(data, str):
            return Bencode.encode(data.encode("ascii"))
        elif isinstance(data, list):
            return b"l" + b"".join(map(Bencode.encode, data)) + b"e"
        elif isinstance(data, dict):
            if all(isinstance(i, bytes) for i in data.keys()):
                items = list(data.items())
                items.sort()
                return b"d" + b"".join(map(Bencode.encode, itertools.chain(*items))) + b"e"
            else:
                raise ValueError("dict keys should be bytes")
        raise ValueError("Allowed types: int, bytes, list, dict; not %s", type(data))

    def decode(data):
        if not isinstance(data, list):
            data = Bencode._tokenize(data)
        if data[0] == b'i':
            return int(data[1].decode())
        elif data[0] == b'd':
            # Each dict can be thought of as list [key,val,key,val]. We just have to remove the colon seperators
            # and call recursively, then do some cleaning to get it in dict format
            data[0] = b'l'
            print(data)
            r = {}
            dict_end = Bencode._find_ending_token(data)
            for token in range(len(data[:dict_end])):
                if data[token] == b':':
                    if not Bencode._is_integer(data[token-1]):
                        del data[token]
                        data.append(b'e')
            # Zipping so we dont have a lot of clutter working through these. Can be improved for performace later
            for key,val in zip(Bencode.decode(data)[0::2], Bencode.decode(data)[1::2]):
                r[key] = val
            return r

        elif data[0] == b'l':
            data = data[1:] + [b'e'] # padding 'hack' so the length is right
            r = []
            start = 0
            while data[start] != b'e':
                end_block = Bencode._find_ending_token(data[start:])+start
                val = Bencode.decode(data[start:end_block+1])
                r.append(val)
                start = end_block+1
            return r
        else:
            return data[2]

    def _find_ending_token(data):
        """ Given a _tokenized data, returns the index of the ending of the first encoded data. """
        if not isinstance(data, list):
            data = Bencode._tokenize(data)
        if data[0] == b'i':
            return 2
        elif data[0] == b'd' or data[0] == b'l':
            count = 0
            for index, token in enumerate(data, start=0):
                if token == b'e':
                    count -= 1
                elif token == b'd' or token == b'l':
                    count += 1
                if count == 0:
                    break
            return index
        else:
            return 2


    def _is_integer(data):
        """ Given a bytestring, returns true if it is a positive integer encoded in ascii"""
        try:
            int(data.decode())
            return True
        except:
            return False

    def _tokenize(data):
        """ Returns the bencode data in a tokenized list. """

        if not isinstance(data, bytes):
            return data

        if data is None or data == b'':
            return []

        ret = []
        data = [bytes([b]) for b in data]

        for index, b in enumerate(data, start=0):
            if b == b'd':
                return [b'd'] + Bencode._tokenize(b''.join(data[index+1:]))

            elif b == b'i':
                offset = 1
                while data[offset] != b'e':
                    offset += 1
                return [b'i'] + [b''.join(data[1:offset])] + Bencode._tokenize(b''.join(data[offset:]))

            elif b == b'l':
                return [b'l'] + Bencode._tokenize(b''.join(data[index+1:]))

            elif b.isdigit():
                offset = 1
                while data[offset].isdigit():
                    offset += 1
                val = int(b''.join(data[:offset]).decode())
                return [b''.join(data[:offset])] + [b':'] + [b''.join(data[offset+1:offset+val+1])] + Bencode._tokenize(b''.join(data[offset+val+1:]))

            elif b == b'e':
                try:
                    return [b'e'] + Bencode._tokenize(b''.join(data[index+1:]))
                except:
                    return [b'e']

            elif b == b':':
                return [b':'] + Bencode._tokenize(b''.join(data[index+1:]))

            else:
                raise ValueError

if __name__ == "__main__":
    # print(Bencode._find_ending_token(b"d3:bar4:spam3:fooi42ee"))
    # print(Bencode.decode(b"l4:spam4:eggsi3ee"))
    print(Bencode.decode(b"de"))
    # print(Bencode.decode(b"llli3eeee"))