import unittest
import os

from eml_analyzer.library.parser import ParsedEmail, EmlParsingException


def load_test_eml_file(test_file) -> str:
    current_directory_of_the_script = os.path.dirname(__file__)
    test_emails = os.path.join(current_directory_of_the_script, 'test_emails')
    path_to_test_file = os.path.join(test_emails, test_file)
    with open(path_to_test_file, mode='r') as input_file:
        return input_file.read()


class TestParsedEmail(unittest.TestCase):
    def test_case_invalid_argument(self):
        try:
            x = ParsedEmail(eml_content=b'ASDKSABD')  # a string is expected
            self.fail(msg="no exception was raised")
        except EmlParsingException:
            pass

    def test_case_1_txt(self):
        expected_text = """This is an HTML message. Please use an HTML capable mail program to read this message. """
        eml_content = load_test_eml_file('file_1.eml')
        x = ParsedEmail(eml_content=eml_content)
        self.assertEqual(x.get_text_content().replace('\n', ' '), expected_text)

    def test_case_1_header_subject(self):
        eml_content = load_test_eml_file('file_1.eml')
        x = ParsedEmail(eml_content=eml_content)
        header = x.get_header()
        for key, value in header:
            if key == 'Subject':
                self.assertIn(value, 'UnitTest Subject =?UTF-8?B?TcO8bmNoZW4s?=')
                return
        self.fail(msg="header subject not found")

    def test_case_1_structure(self):
        eml_content = load_test_eml_file('file_1.eml')
        x = ParsedEmail(eml_content=eml_content)
        structure = x.get_structure()
        self.assertEqual(structure.filename, None)
        self.assertEqual(structure.content_type, 'multipart/mixed')
        self.assertEqual(structure.content_disposition, None)

        self.assertEqual(structure.child_items[0].filename, None)
        self.assertEqual(structure.child_items[0].content_type, 'multipart/related')
        self.assertEqual(structure.child_items[0].content_disposition, None)

        self.assertEqual(structure.child_items[0].child_items[0].filename, None)
        self.assertEqual(structure.child_items[0].child_items[0].content_type, 'multipart/alternative')
        self.assertEqual(structure.child_items[0].child_items[0].content_disposition, None)

        self.assertEqual(structure.child_items[0].child_items[0].child_items[0].filename, None)
        self.assertEqual(structure.child_items[0].child_items[0].child_items[0].content_type, 'text/plain')
        self.assertEqual(structure.child_items[0].child_items[0].child_items[0].content_disposition, None)

        self.assertEqual(structure.child_items[0].child_items[0].child_items[1].filename, None)
        self.assertEqual(structure.child_items[0].child_items[0].child_items[1].content_type, 'text/html')
        self.assertEqual(structure.child_items[0].child_items[0].child_items[1].content_disposition, None)

        self.assertEqual(structure.child_items[1].filename, 'attachment.txt')
        self.assertEqual(structure.child_items[1].content_type, 'text/plain')
        self.assertEqual(structure.child_items[1].content_disposition, 'attachment')

    def test_case_1_attachments(self):
        eml_content = load_test_eml_file('file_1.eml')
        x = ParsedEmail(eml_content=eml_content)
        attachments = x.get_attachments()
        self.assertEqual(len(attachments), 3)

        self.assertEqual(attachments[0].filename, 'logo.gif')
        self.assertEqual(attachments[0].content_type, 'image/gif')
        self.assertEqual(attachments[0].content_disposition, 'inline')

        self.assertEqual(attachments[1].filename, 'background.gif')
        self.assertEqual(attachments[1].content_type, 'image/gif')
        self.assertEqual(attachments[1].content_disposition, 'inline')

        self.assertEqual(attachments[2].filename, 'attachment.txt')
        self.assertEqual(attachments[2].content_type, 'text/plain')
        self.assertEqual(attachments[2].content_disposition, 'attachment')

    def test_case_1_reloaded_content_from_html(self):
        eml_content = load_test_eml_file('file_1.eml')
        x = ParsedEmail(eml_content=eml_content)
        reloaded_content_from_html = x.get_reloaded_content_from_html()
        self.assertIn('https://www.reloaded-domain.com/abc.png', reloaded_content_from_html)

    def test_case_1_embedded_urls(self):
        eml_content = load_test_eml_file('file_1.eml')
        x = ParsedEmail(eml_content=eml_content)
        embedded_urls = x.get_embedded_urls_from_html_and_text()
        self.assertEqual(len(embedded_urls), 2)
        self.assertIn('https://test-link2.com', embedded_urls)
        self.assertIn('https://www.unittest.de/test', embedded_urls)

    def test_case_1_parser_reloaded_content(self):
        reloaded_content_from_html = ParsedEmail._get_reloaded_content_from_html(html="""
        <img src=3D"cid:ae0357e57f04b8347f7621662cb63855.gif">
        <a class="clearLink" href="https://test-link2.com"/>
        <img src="https://www.reloaded-domain.com/abc.png"/>
        """)
        self.assertEqual(len(reloaded_content_from_html), 1)
        self.assertIn('https://www.reloaded-domain.com/abc.png', reloaded_content_from_html)

    def test_case_1_parser_embedded_urls_from_html(self):
        embedded_urls = ParsedEmail._get_embedded_urls_from_html(html="""
        https://www.unittest.de/test
        <img src=3D"cid:ae0357e57f04b8347f7621662cb63855.gif">
        <a class="clearLink" href="https://test-link2.com"/>
        <img src="https://www.reloaded-domain.com/abc.png"/>
        """)
        self.assertEqual(len(embedded_urls), 1)
        self.assertIn('https://test-link2.com', embedded_urls)

    def test_case_1_parser_embedded_urls_from_text(self):
        # if there is no protocol in front of an URL e.g. Outlook does not make it clickable for the user.
        # So "facebook.com/asdasd" is out of the scope to be detected. Also a detection for this would probably lead to many false positives.
        embedded_urls = ParsedEmail._get_embedded_urls_from_text(text="""
        https://www.unittest.de/test
        <a class="clearLink" href="https://test-link2.com"/>
        facebook.com/asdasd
        """)
        self.assertEqual(len(embedded_urls), 2)
        self.assertIn('https://www.unittest.de/test', embedded_urls)
        self.assertIn('https://test-link2.com', embedded_urls)
