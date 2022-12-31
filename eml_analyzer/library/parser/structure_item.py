import email
from eml_analyzer.library.parser.printable_filename import get_printable_filename_if_existent


class StructureItem:
    def __init__(self, message: email.message.Message):
        self.content_type = message.get_content_type()
        self.filename: str or None = get_printable_filename_if_existent(message=message)
        self.content_disposition: str or None = message.get_content_disposition()

        self.child_items = list()
        if message.is_multipart():
            for child in message.get_payload():
                self.child_items.append(StructureItem(message=child))
