import email.message
from eml_analyzer.library.parser.printable_filename import get_printable_filename_if_existent


class Attachment:
    def __init__(self, message: email.message.Message, index: int):
        self.index: int = index
        self.filename: str or None = get_printable_filename_if_existent(message=message)
        self.content_type: str = message.get_content_type()
        self.content_disposition: str = message.get_content_disposition()
        self.content: bytes = message.get_payload(decode=True)
