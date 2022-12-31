import unittest

from eml_analyzer.library.parser import StructureItem


class messageMock:
    def __init__(self, filename: str or None):
        self.filename = filename
        self.children = list()

    def get_filename(self):
        return self.filename

    def get_content_type(self):
        return "content_type"

    def get_content_disposition(self):
        return "content_disposition"

    def is_multipart(self) -> bool:
        return len(self.children) > 0

    def get_payload(self):
        return self.children


class TestPrintableFilename(unittest.TestCase):
    def test_case_1(self):
        message = messageMock(filename="filename")
        structure_item = StructureItem(message=message)
        self.assertEqual(structure_item.filename, "filename")
        self.assertEqual(structure_item.content_type, "content_type")
        self.assertEqual(structure_item.content_disposition, "content_disposition")

    def test_case_2(self):
        child_1 = messageMock(filename="child_1")
        child_2 = messageMock(filename="child_2")

        parent_message = messageMock(filename="parent")
        parent_message.children.append(child_1)
        parent_message.children.append(child_2)

        structure_item = StructureItem(message=parent_message)
        self.assertEqual(structure_item.filename, "parent")
        self.assertEqual(structure_item.child_items[0].filename, "child_1")
        self.assertEqual(structure_item.child_items[1].filename, "child_2")
