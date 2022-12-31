import base64
import binascii
import re
import email.message


def get_printable_filename_if_existent(message: email.message.Message) -> str or None:
    filename = message.get_filename()
    if filename is None:
        return None
    return _make_string_printable(original_string=filename)


def _make_string_printable(original_string: str) -> str:
    original_string = _decode_ASCII_encoded_UTF8_string(string=original_string)

    additional_allowed_chars = {'_', '.', '(', ')', '-', ' '}
    clean_name = ''
    for x in original_string:
        if x.isalpha() or x.isalnum() or x in additional_allowed_chars:
            clean_name += x
        elif x.isprintable():
            clean_name += '_'
    return clean_name


def _decode_ASCII_encoded_UTF8_string(string: str) -> str:
    """ decodes ASCII strings which are encoded like: name := "=?UTF-8?B?" + base64_encode(string) + "?=" """
    pattern = re.compile(r'=\?utf-8\?B\?(.+?)\?=', re.IGNORECASE)
    for match in list(re.finditer(pattern=pattern, string=string)):
        try:
            string = string.replace(match.group(0), base64.b64decode(match.group(1)).decode('utf-8'))
        except binascii.Error:
            pass
    return string
