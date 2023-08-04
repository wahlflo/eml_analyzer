import base64
import binascii
import re
import email.message
import quopri


def get_printable_filename_if_existent(message: email.message.Message) -> str or None:
    filename = message.get_filename()
    if filename is None:
        return None
    return _make_string_printable(original_string=filename)


def _make_string_printable(original_string: str) -> str:
    original_string = decode_ASCII_encoded_string(string=original_string)

    additional_allowed_chars = {'_', '.', '(', ')', '-', ' '}
    clean_name = ''
    for x in original_string:
        if x.isalpha() or x.isalnum() or x in additional_allowed_chars:
            clean_name += x
        elif x.isprintable():
            clean_name += '_'
    return clean_name


def decode_ASCII_encoded_string(string: str) -> str:
    string = _decode_ASCII_encoded_string_baseX(string=string)
    string = _decode_ASCII_encoded_string_quoted_printable_string(string=string)
    return string


def _decode_ASCII_encoded_string_baseX(string: str) -> str:
    """ decodes ASCII strings which are encoded like: name := "=?UTF-8?B?" + base64_encode(string) + "?=" """
    pattern = re.compile(r'=\?(.+?)\?B\?(.+?)\?=', re.IGNORECASE)
    for match in list(re.finditer(pattern=pattern, string=string)):
        try:
            string = string.replace(match.group(0), base64.b64decode(match.group(2)).decode(match.group(1)))
        except binascii.Error:
            pass
    return string


def _decode_ASCII_encoded_string_quoted_printable_string(string: str) -> str:
    pattern = re.compile(r'=\?(.+?)\?Q\?(.+?)\?=', re.IGNORECASE)
    for match in list(re.finditer(pattern=pattern, string=string)):
        try:
            encoding = match.group(1)
            encoded_string = match.group(2)
            decoded_string = quopri.decodestring(encoded_string)
            replacement = decoded_string.decode(encoding)
            string = string.replace(match.group(0), replacement)
        except binascii.Error:
            pass
    return string
