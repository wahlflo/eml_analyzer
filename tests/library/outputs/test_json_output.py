import json
import unittest
from typing import List, Tuple

from eml_analyzer.library.outputs import JsonOutput
from eml_analyzer.library.parser import Attachment, StructureItem


class TestJsonOutput(unittest.TestCase):
    def test_case_header(self):
        class parsedEmailMock:
            def get_header(self) -> List[Tuple[str, any]]:
                return [
                    ('key 1', 'value a'),
                    ('key 1', 'value b'),
                    ('key 2', 'value c'),
                ]

            def get_error_messages(self) -> List[str]:
                return list()

        output = JsonOutput()
        output.process_option_show_header(parsed_email=parsedEmailMock())
        output = output.get_final_output(parsed_email=parsedEmailMock())
        output = json.loads(output)
        self.assertIn('headers', output)
        self.assertIn('key 1', output['headers'])
        self.assertIn('key 2', output['headers'])
        self.assertIn('value a', output['headers']['key 1'])
        self.assertIn('value b', output['headers']['key 1'])
        self.assertIn('value c', output['headers']['key 2'])

    def test_case_structure(self):
        class structureItemMock:
            def __init__(self, content_type: str):
                self.content_type = content_type
                self.filename = None
                self.content_disposition = None
                self.child_items = list()

        class parsedEmailMock:
            def get_structure(self):
                node_0 = structureItemMock(content_type="multipart/mixed")

                node_1 = structureItemMock(content_type="multipart/related")
                node_0.child_items.append(node_1)

                node_2 = structureItemMock(content_type="multipart/alternative")
                node_1.child_items.append(node_2)

                node_3a = structureItemMock(content_type="text/plain")
                node_2.child_items.append(node_3a)
                node_3b = structureItemMock(content_type="text/html")
                node_2.child_items.append(node_3b)

                node_4 = structureItemMock(content_type="text/plain")
                node_4.filename = 'attachment.txt'
                node_4.content_disposition = 'attachment'
                node_0.child_items.append(node_4)

                return node_0

            def get_error_messages(self) -> List[str]:
                return list()

        output = JsonOutput()
        output.process_option_show_structure(parsed_email=parsedEmailMock())
        output = output.get_final_output(parsed_email=parsedEmailMock())
        output = json.loads(output)
        self.assertIn('structure', output)
        structure = output['structure']

        self.assertNotIn('disposition', structure)
        self.assertIn('type', structure)
        self.assertEqual(structure['type'], "multipart/mixed")
        self.assertIn('children', structure)

        structure = structure['children']
        attachment = structure[1]
        structure = structure[0]
        self.assertNotIn('disposition', structure)
        self.assertIn('type', structure)
        self.assertEqual(structure['type'], "multipart/related")
        self.assertIn('children', structure)

        structure = structure['children']
        self.assertEqual(len(structure), 1)

        self.assertEqual(len(structure[0]['children']), 2)

        self.assertEqual(attachment['name'], 'attachment.txt')
        self.assertEqual(attachment['disposition'], 'attachment')

    def test_case_show_html(self):
        class parsedEmailMock:
            def __init__(self, html):
                self.html = html

            def get_html_content(self):
                return self.html

            def get_error_messages(self) -> List[str]:
                return list()

        output = JsonOutput()
        output.process_option_show_html(parsed_email=parsedEmailMock(html=None))
        output = output.get_final_output(parsed_email=parsedEmailMock(html=None))
        output = json.loads(output)
        self.assertNotIn('html', output)

        output = JsonOutput()
        output.process_option_show_html(parsed_email=parsedEmailMock(html="test"))
        output = output.get_final_output(parsed_email=parsedEmailMock(html="test"))
        output = json.loads(output)
        self.assertIn('html', output)
        self.assertEqual(output['html'], "test")

    def test_case_show_text(self):
        class parsedEmailMock:
            def __init__(self, text):
                self.text = text

            def get_text_content(self):
                return self.text

            def get_error_messages(self) -> List[str]:
                return list()

        output = JsonOutput()
        output.process_option_show_text(parsed_email=parsedEmailMock(text=None))
        output = output.get_final_output(parsed_email=parsedEmailMock(text=None))
        output = json.loads(output)
        self.assertNotIn('text', output)

        output = JsonOutput()
        output.process_option_show_text(parsed_email=parsedEmailMock(text="test"))
        output = output.get_final_output(parsed_email=parsedEmailMock(text="test"))
        output = json.loads(output)
        self.assertIn('text', output)
        self.assertEqual(output['text'], "test")

    def test_show_embedded_urls_in_html_and_text(self):
        class parsedEmailMock:
            def get_embedded_clickable_urls_from_html_and_text(self):
                return ["test_1", "test_2"]

            def get_error_messages(self) -> List[str]:
                return list()

        output = JsonOutput()
        output.process_option_show_embedded_urls_in_html_and_text(parsed_email=parsedEmailMock())
        output = output.get_final_output(parsed_email=parsedEmailMock())
        output = json.loads(output)
        self.assertIn('urls', output)
        self.assertEqual(len(output['urls']), 2)
        self.assertIn("test_1", output['urls'])
        self.assertIn("test_2", output['urls'])

    def test_process_option_show_attachments(self):
        class mockAttachment:
            def __init__(self, filename: str):
                self.content_type = "text/plain"
                self.filename = filename
                self.content_disposition = "attachment"

        class parsedEmailMock:
            def get_attachments(self) -> List[mockAttachment]:
                return [mockAttachment("file_1"), mockAttachment("file_2")]

            def get_error_messages(self) -> List[str]:
                return list()

        output = JsonOutput()
        output.process_option_show_attachments(parsed_email=parsedEmailMock(), extract_content=False)
        output = output.get_final_output(parsed_email=parsedEmailMock())
        output = json.loads(output)
        self.assertIn('attachments', output)
        self.assertEqual(len(output['attachments']), 2)
        self.assertEqual(output['attachments'][0]['name'], "file_1")
        self.assertEqual(output['attachments'][0]['type'], "text/plain")
        self.assertEqual(output['attachments'][0]['disposition'], "attachment")
        self.assertEqual(output['attachments'][1]['name'], "file_2")

    def test_process_option_show_reloaded_content_from_html(self):
        class parsedEmailMock:
            def get_reloaded_content_from_html(self):
                return ["test_1", "test_2"]

            def get_error_messages(self) -> List[str]:
                return list()

        output = JsonOutput()
        output.process_option_show_reloaded_content_from_html(parsed_email=parsedEmailMock())
        output = output.get_final_output(parsed_email=parsedEmailMock())
        output = json.loads(output)
        self.assertIn('reloaded_content', output)
        self.assertEqual(len(output['reloaded_content']), 2)
        self.assertIn("test_1", output['reloaded_content'])
        self.assertIn("test_2", output['reloaded_content'])
