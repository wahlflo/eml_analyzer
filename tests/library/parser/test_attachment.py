import unittest

from eml_analyzer.library.parser import Attachment
from eml_analyzer.library.parser.printable_filename import get_printable_filename_if_existent, _make_string_printable, _decode_ASCII_encoded_UTF8_string


class messageMock:
    def __init__(self, filename: str, payload: bytes):
        self.filename = filename
        self.payload = payload

    def get_filename(self):
        return self.filename

    def get_content_type(self):
        return "content_type"

    def get_content_disposition(self):
        return "content_disposition"

    def get_payload(self, decode: bool):
        return self.payload


class TestAttachment(unittest.TestCase):
    def test_case_1(self):
        attachment = Attachment(message=messageMock(filename='filename', payload=b''), index=0)
        self.assertEqual(attachment.filename, 'filename')
        self.assertEqual(attachment.content_type, 'content_type')
        self.assertEqual(attachment.content_disposition, 'content_disposition')

    def test_payload_base64_encoding(self):
        attachment = Attachment(message=messageMock(filename='filename', payload=b'HELLO WORLD'), index=0)
        self.assertEqual(attachment.get_content_base64_encoded(), 'SEVMTE8gV09STEQ=')
