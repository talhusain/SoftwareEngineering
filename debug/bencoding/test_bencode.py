import unittest
from . import bencode

class TestEncode(unittest.TestCase):

    def test_string(self):
        """ Test strings are encoded correctly. """

        self.n = bencode.Bencode.encode(b"test")
        self.assertEqual(self.n, b"4:test")

    def test_empty__string(self):
        """ Test empty strings are encoded correctly. """
    
        self.n = bencode.Bencode.encode(b"")
        self.assertEqual(self.n, b"0:")

    def test_integer(self):
        """ Test integers are encoded correctly. """

        self.n = bencode.Bencode.encode(42)
        self.assertEqual(self.n, b"i42e")

    def test_negative_integer(self):
        """ Test negative integers are encoded correctly. """

        self.n = bencode.Bencode.encode(-42)
        self.assertEqual(self.n, b"i-42e")

    def test_zero(self):
        """ Test zero is encoded correctly. """

        self.n = bencode.Bencode.encode(0)
        self.assertEqual(self.n, b"i0e")

    @unittest.skip("To be implemented later")
    def test_negative_zero(self):
        """ Test encoding negative zero raises an exception. """

        with self.assertRaises(ValueError):
            bencode.Bencode.encode("i-0e")

    def test_dict(self):
        """ Test dictionaries are encoded correctly. """

        self.n = bencode.Bencode.encode({b"bar": b"spam", b"foo": 42})
        self.assertEqual(self.n, b"d3:bar4:spam3:fooi42ee")

    @unittest.skip("To be implemented later")
    def test_dict_keys_are_ordered(self):
        """ Test dictionary keys are in sorted order. """
        pass

    def test_empty_dict(self):
        """ Test empty dictionaries are encoded correctly. """

        self.n = bencode.Bencode.encode({})
        self.assertEqual(self.n, b"de")

    def test_nested_dicts(self):
        """ Test nested dictionaries are encoded correctly. """

        self.n = bencode.Bencode.encode({b"":{b"":b"test"}})
        self.assertEqual(self.n, b"d0:d0:4:testee")

    def test_list(self):
        """ Test lists are encoded correctly. """

        self.n = bencode.Bencode.encode([b"spam", b"eggs", 3])
        self.assertEqual(self.n, b"l4:spam4:eggsi3ee")

    def test_empty_list(self):
        """ Test empty lists are encoded correctly. """

        self.n = bencode.Bencode.encode([])
        self.assertEqual(self.n, b"le")

    def test_nested_lists(self):
        """ Test nested lists are encoded correctly. """

        self.n = bencode.Bencode.encode([b"spam", b"eggs", [3]])
        self.assertEqual(self.n, b"l4:spam4:eggsli3eee")

    def test_list_inside_dict(self):
        """ Test lists inside dictionaries are encoded correctly. """

        self.n = bencode.Bencode.encode({b"spam":[b"a", b"b"]})
        self.assertEqual(self.n, b"d4:spaml1:a1:bee")

    def test_dict_inside_list(self):
        """ Test dictionaries inside lists are encoded correctly. """

        self.n = bencode.Bencode.encode([{b"spam":[b"a", b"b"]}])
        self.assertEqual(self.n, b"ld4:spaml1:a1:beee")


class TestDecode(unittest.TestCase):

    def test_string(self):
        """ Test strings are decoded correctly. """
    
        self.n = bencode.Bencode.decode(b"4:test")
        self.assertEqual(self.n, b"test")

    def test_empty_string(self):
        """ Test empty strings are decoded correctly. """
    
        self.n = bencode.Bencode.decode(b"0:")
        self.assertEqual(self.n, b"")

    def test_integer(self):
        """ Test integers are decoded correctly. """

        self.n = bencode.Bencode.decode(b"i42e")
        self.assertEqual(self.n, 42)

    @unittest.skip("To be implemented later")
    def test_integer_for_leading_zeros(self):
        """ Test integers with a leading zero raise an exception. """

        with self.assertRaises(ValueError):
            bencode.Bencode.decode(b"i042e")

    def test_negative_integer(self):
        """ Test negative integers are decoded correctly. """

        self.n = bencode.Bencode.decode(b"i-42e")
        self.assertEqual(self.n, -42)

    def test_zero(self):
        """ Test zero is decoded correctly. """

        self.n = bencode.Bencode.decode(b"i0e")
        self.assertEqual(self.n, 0)

    def test_dict(self):
        """ Test dictionaries are decoded correctly. """

        self.n = bencode.Bencode.decode(b"d3:bar4:spam3:fooi42ee")
        self.assertEqual(self.n, {b"bar": b"spam", b"foo": 42})

    def test_empty_dict(self):
        """ Test empty dictionaries are decoded correctly. """

        self.n = bencode.Bencode.decode(b"de")
        self.assertEqual(self.n, {})

    def test_nested_dicts(self):
        """ Test nested dictionaries are decoded correctly. """

        self.n = bencode.Bencode.decode(b"d0:d4:test:i42eee")
        self.assertEqual(self.n, {b"":{b"test":42}})

    def test_list(self):
        """ Test lists are decoded correctly. """

        self.n = bencode.Bencode.decode(b"l4:spam4:eggsi3ee")
        self.assertEqual(self.n, [b"spam", b"eggs", 3])

    def test_empty_list(self):
        """ Test empty lists are decoded correctly. """

        self.n = bencode.Bencode.decode(b"le")
        self.assertEqual(self.n, [])

    def test_nested_lists(self):
        """ Test nested lists are decoded correctly. """

        self.n = bencode.Bencode.decode(b"l4:spam4:eggsli3eee")
        self.assertEqual(self.n, [b"spam", b"eggs", [3]])

    def test_list_inside_dict(self):
        """ Test lists inside dictionaries are decoded correctly. """

        self.n = bencode.Bencode.decode(b"d4:spaml1:a1:bee")
        self.assertEqual(self.n, {b"spam":[b"a", b"b"]})

    def test_dict_inside_list(self):
        """ Test dictionaries inside lists are decoded correctly. """

        self.n = bencode.Bencode.decode(b"ld4:spaml1:a1:beee")
        self.assertEqual(self.n, [{b"spam":[b"a", b"b"]}])


class TestTokenize(unittest.TestCase):

    def test_string(self):
        """ Test strings are tokenized correctly. """
    
        self.n = bencode.Bencode._tokenize(b"4:test")
        self.assertEqual(self.n, [b"4", b":", b"test"])

    def test_integer(self):
        """ Test integers are tokenized correctly. """
    
        self.n = bencode.Bencode._tokenize(b"i3e")
        self.assertEqual(self.n, [b"i", b"3", b"e"])

    def test_negative_integer(self):
        """ Test negative integers are tokenized correctly. """
    
        self.n = bencode.Bencode._tokenize(b"i-3e")
        self.assertEqual(self.n, [b"i", b"-3", b"e"])

    def test_zero(self):
        """ Test zeros are tokenized correctly. """
    
        self.n = bencode.Bencode._tokenize(b"i0e")
        self.assertEqual(self.n, [b"i", b"0", b"e"])

    def test_list(self):
        """ Test lists are tokenized correctly. """

        self.n = bencode.Bencode._tokenize(b"l12:testtesttest4:asdfi3ee")
        self.assertEqual(self.n, [b'l', b'12', b':', b'testtesttest', b'4', b':', b'asdf', b'i', b'3', b'e', b'e'])

    def test_empty_list(self):
        """ Test empty lists are tokenized correctly. """

        self.n = bencode.Bencode._tokenize(b"le")
        self.assertEqual(self.n, [b'l', b'e'])

    def test_dict(self):
        """ Test dictionaries are tokenized correctly. """

        self.n = bencode.Bencode._tokenize(b"d3:bar4:spam3:fooi42ee")
        self.assertEqual(self.n, [b'd', b'3', b':', b'bar', b'4', b':', b'spam', b'3', b':', b'foo', b'i', b'42', b'e', b'e'])

    def test_empty_dict(self):
        """ Test empty dictionaries are tokenized correctly. """

        self.n = bencode.Bencode._tokenize(b"de")
        self.assertEqual(self.n, [b'd', b'e'])

    def test_malformed_data(self):
        """ Test bad data raises an exception. """

        with self.assertRaises(ValueError):
            bencode.Bencode._tokenize(b"asdfasdfifniubcbiufdcnlsakjcabfuqiwegfqwhbcalsdcalsdkf")


if __name__ == '__main__':
    unittest.main()