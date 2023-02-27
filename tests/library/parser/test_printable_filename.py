import unittest

from eml_analyzer.library.parser.printable_filename import get_printable_filename_if_existent, _make_string_printable, _decode_ASCII_encoded_string


class TestPrintableFilename(unittest.TestCase):
    def test_decode_ASCII_encoded_string(self):
        # [(value, expected)]
        test_cases = [
            ('', ''),
            ('Hello World', 'Hello World'),
            ('=?UTF-8?B?4o6Y7Z+/?=', '⎘퟿'),
            ('=?utf-8?b?4o6Y7Z+/?=', '⎘퟿'),
            ('=?utf-16?b?SABlAGwAbABvAFcAbwByAGwAZAA=?=', 'HelloWorld'),
        ]
        for value, expected in test_cases:
            result = _decode_ASCII_encoded_string(string=value)
            self.assertEqual(result, expected)

    def test_make_string_printable(self):
        # [(value, expected)]
        test_cases = [
            ('', ''),
            ('Hello World', 'Hello World'),
            ('=?UTF-8?B?7Z+/?=', ''),  # character is not printable
            ('=?UTF-8?B?4o6Y?=', '_'),  # character is printable
        ]
        for value, expected in test_cases:
            result = _make_string_printable(original_string=value)
            self.assertEqual(result, expected)

    def test_get_printable_filename_if_existent(self):
        # [(value, expected)]
        test_cases = [
            ('', ''),
            ('Hello World', 'Hello World'),
            ('=?UTF-8?B?7Z+/?=', ''),  # character is not printable
            ('=?UTF-8?B?4o6Y?=', '_'),  # character is printable
            (None, None),
        ]

        class MessageMock:
            def __init__(self, value: str):
                self.value = value

            def get_filename(self) -> str:
                return self.value

        for value, expected in test_cases:
            result = get_printable_filename_if_existent(message=MessageMock(value=value))
            self.assertEqual(result, expected)
