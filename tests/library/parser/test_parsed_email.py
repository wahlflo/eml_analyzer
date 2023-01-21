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

    def test_embedded_urls_case_1(self):
        eml_content = load_test_eml_file('file_1.eml')
        x = ParsedEmail(eml_content=eml_content)
        embedded_urls = x.get_embedded_clickable_urls_from_html_and_text()
        self.assertEqual(len(embedded_urls), 2)
        self.assertIn('https://test-link2.com', embedded_urls)
        self.assertIn('https://www.unittest.de/test', embedded_urls)

    def test_embedded_urls_case_2(self):
        eml_content = load_test_eml_file('file_2.eml')
        x = ParsedEmail(eml_content=eml_content)
        embedded_urls = x.get_embedded_clickable_urls_from_html_and_text()

        self.assertEqual(5, len(embedded_urls))
        self.assertIn('https://embedded-url.com', embedded_urls)
        self.assertIn('https://twitter.com/', embedded_urls)
        self.assertIn('https://carleton.ca/', embedded_urls)
        self.assertIn('https://nam12.safelinks.protection.outlook.com/?url=https://twitter.com/&data=05|01|admin@tq2zr.onmicrosoft.com|49360182de73427cd8e908dae851e772|71759330a027406e9082f1f64f1007b3|0|0|638077735753161743|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0=|3000|||&sdata=YF3Fdvo0FyHQkXoHuhv3WzGzfhmqGjCRMdxUPIZsYvA=&reserved=0', embedded_urls)
        self.assertIn('https://nam12.safelinks.protection.outlook.com/?url=https://carleton.ca/&data=05|01|admin@tq2zr.onmicrosoft.com|49360182de73427cd8e908dae851e772|71759330a027406e9082f1f64f1007b3|0|0|638077735753161743|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0=|3000|||&sdata=49SuRO9jfbmE5QmGqq85RvUZgZnyJ6XgFjlD3V7duYw=&reserved=0', embedded_urls)

    def test_parser_embedded_urls_from_text_case_1(self):
        # if there is no protocol in front of a URL e.g. Outlook does not make it clickable for the user.
        # So "facebook.com/asdasd" is out of the scope to be detected. Also, a detection for this would probably lead to many false positives.
        embedded_urls = ParsedEmail._get_embedded_urls_from_text(text="""
        https://www.unittest.de/test
        <a class="clearLink" href="https://test-link2.com"/>
        facebook.com/asdasd
        """)
        self.assertEqual(len(embedded_urls), 2)
        self.assertIn('https://www.unittest.de/test', embedded_urls)
        self.assertIn('https://test-link2.com', embedded_urls)

    def test_parser_embedded_urls_from_text_case_2(self):
        """ tested in Outlook. Outlook makes the string "https://carleton.ca/</a></span></div>" clickable """
        found_urls = ParsedEmail._get_embedded_urls_from_text(text="""https://carleton.ca/</a></span></div>""")
        self.assertEqual(1, len(found_urls))
        self.assertIn('https://carleton.ca/</a></span></div>', found_urls)
    def test_parser_embedded_urls_from_text_case_3(self):
        """ tested in Outlook. Outlook makes the string "https://carleton.ca/"</a></span></div>" clickable """
        found_urls = ParsedEmail._get_embedded_urls_from_text(text="""link: "https://carleton.ca/"</a></span></div>""")
        self.assertEqual(1, len(found_urls))
        self.assertIn('https://carleton.ca/"</a></span></div>', found_urls)

    def test_parser_embedded_clickable_urls_from_html_links_case_1(self):
        embedded_urls = ParsedEmail._get_embedded_clickable_urls_from_html_links(html_data="""
        https://www.unittest.de/test
        <img src=3D"cid:ae0357e57f04b8347f7621662cb63855.gif">
        <a class="clearLink" href="https://test-link2.com"/>
        <img src="https://www.reloaded-domain.com/abc.png"/>
        """)
        embedded_urls = {x.url for x in embedded_urls}
        self.assertEqual(len(embedded_urls), 1)
        self.assertIn('https://test-link2.com', embedded_urls)

    def test_parser_embedded_clickable_urls_from_html_links_case_2(self):
        embedded_urls = ParsedEmail._get_embedded_clickable_urls_from_html_links(html_data="""
        <html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<style type="text/css" style="display:none;"> P {margin-top:0;margin-bottom:0;} </style>
</head>
<body dir="ltr">
<div class="elementToProof" style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);">
<span style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);"><span class="x_elementToProof FluidPluginCopy" style="font-size:15px;font-family:&quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif;margin:0px;color:rgb(36, 36, 36);background-color:rgb(255, 255, 255)"><span style="font-size:12pt;font-family:Calibri, Arial, Helvetica, sans-serif;margin:0px;color:rgb(0, 0, 0);background-color:rgb(255, 255, 255)"><a href="https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Ftwitter.com%2F&amp;data=05%7C01%7Cadmin%40tq2zr.onmicrosoft.com%7C49360182de73427cd8e908dae851e772%7C71759330a027406e9082f1f64f1007b3%7C0%7C0%7C638077735753161743%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&amp;sdata=YF3Fdvo0FyHQkXoHuhv3WzGzfhmqGjCRMdxUPIZsYvA%3D&amp;reserved=0" originalsrc="https://twitter.com/" shash="qzkaBC2sLxgP1TgKDzZQ22fgeb1b7BsI5lFHyR43eYo7m7MI1zAsITkXPZdZ6n1KIL8l5zsW9ZYym8Zh696/mItL4iYvJ0Ubwz1de7W+ONeLI4b2ew0tg4HzBWjz70b4QTUpxwi7deoO2c/HOahf1M884A1dPLtJtc8s+ZBrhcA=" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="0" style="margin:0px" class="ContentPasted0">https://twitter.com/</a></span></span>
<div class="x_elementToProof FluidPluginCopy" style="font-size:15px;font-family:&quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif;margin:0px;color:rgb(36, 36, 36);background-color:rgb(255, 255, 255)">
<span style="font-size:12pt;font-family:Calibri, Arial, Helvetica, sans-serif;margin:0px;color:rgb(0, 0, 0);background-color:rgb(255, 255, 255)"><br class="ContentPasted0">
</span></div>
<div class="x_elementToProof FluidPluginCopy" style="font-size:15px;font-family:&quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif;margin:0px;color:rgb(36, 36, 36);background-color:rgb(255, 255, 255)">
<span style="font-size:12pt;font-family:Calibri, Arial, Helvetica, sans-serif;margin:0px;color:rgb(0, 0, 0);background-color:rgb(255, 255, 255)"><a href="https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Fcarleton.ca%2F&amp;data=05%7C01%7Cadmin%40tq2zr.onmicrosoft.com%7C49360182de73427cd8e908dae851e772%7C71759330a027406e9082f1f64f1007b3%7C0%7C0%7C638077735753161743%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&amp;sdata=49SuRO9jfbmE5QmGqq85RvUZgZnyJ6XgFjlD3V7duYw%3D&amp;reserved=0" originalsrc="https://carleton.ca/" shash="Dxc62cEP1Yg+/wKXMo/VoujSwhva4+Frdv2Yr8iQuG/kuzsq8b6WfRRSuA3H0L4B+GRsbWHMjTjX4Mg2/0vuwo9UW9HOglt0hd7TcsPjzwi8IgUT3bVowbeQfPFAoMMdOWkKIzbKe4Ax/2E4rJf8j/m4b+N+/72C5VvaPLBgd+8=" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="2" style="margin:0px" class="ContentPasted0">https://carleton.ca/</a></span></div>
<br>
https://embedded_url.com
</span></div>
<div class="elementToProof" style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);">
<span style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);"><img style="max-width: 100%;" class="w-240 h-240" size="6492" contenttype="image/png" data-outlook-trace="F:1|T:1" src="cid:d2eb1b04-21d5-4a18-bfdb-12c4c3e65b8a"><br>
</span></div>
</body>
</html>
        """)
        found_urls = {x.url for x in embedded_urls}
        self.assertEqual(4, len(embedded_urls))
        self.assertIn('https://nam12.safelinks.protection.outlook.com/?url=https://twitter.com/&data=05|01|admin@tq2zr.onmicrosoft.com|49360182de73427cd8e908dae851e772|71759330a027406e9082f1f64f1007b3|0|0|638077735753161743|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0=|3000|||&sdata=YF3Fdvo0FyHQkXoHuhv3WzGzfhmqGjCRMdxUPIZsYvA=&reserved=0', found_urls)
        self.assertIn('https://nam12.safelinks.protection.outlook.com/?url=https://carleton.ca/&data=05|01|admin@tq2zr.onmicrosoft.com|49360182de73427cd8e908dae851e772|71759330a027406e9082f1f64f1007b3|0|0|638077735753161743|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0=|3000|||&sdata=49SuRO9jfbmE5QmGqq85RvUZgZnyJ6XgFjlD3V7duYw=&reserved=0', found_urls)
        self.assertIn('https://carleton.ca/', found_urls)
        self.assertIn('https://twitter.com/', found_urls)
    def test_parser_embedded_clickable_urls_from_html_case_1(self):
        found_urls = ParsedEmail._get_embedded_clickable_urls_from_html(html_data="""
        <html>
<span style="font-size:12pt;font-family:Calibri, Arial, Helvetica, sans-serif;margin:0px;color:rgb(0, 0, 0);background-color:rgb(255, 255, 255)"><a href="https://nam12.safelinks.protection.outlook.com/" originalsrc="https://carleton.ca/">https://carleton.ca/</a></span></div>
<br>
https://embedded-url.com
</span></div>
</body>
</html>
        """)
        self.assertEqual(3, len(found_urls))
        self.assertIn('https://carleton.ca/', found_urls)
        self.assertIn('https://nam12.safelinks.protection.outlook.com/', found_urls)
        self.assertIn('https://embedded-url.com', found_urls)

    def test_parser_reloaded_content_case_1(self):
        reloaded_content_from_html = ParsedEmail._get_reloaded_content_from_html(html_data="""
        <img src=3D"cid:ae0357e57f04b8347f7621662cb63855.gif">
        <a class="clearLink" href="https://test-link2.com"/>
        <img src="https://www.reloaded-domain.com/abc.png"/>
        """)
        self.assertEqual(1, len(reloaded_content_from_html))
        self.assertIn('https://www.reloaded-domain.com/abc.png', reloaded_content_from_html)

    def test_get_reloaded_content_from_html_case_2(self):
        embedded_urls = ParsedEmail._get_reloaded_content_from_html(html_data="""
        <html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<style type="text/css" style="display:none;"> P {margin-top:0;margin-bottom:0;} </style>
</head>
<body dir="ltr">
<div class="elementToProof" style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);">
<span style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);"><span class="x_elementToProof FluidPluginCopy" style="font-size:15px;font-family:&quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif;margin:0px;color:rgb(36, 36, 36);background-color:rgb(255, 255, 255)"><span style="font-size:12pt;font-family:Calibri, Arial, Helvetica, sans-serif;margin:0px;color:rgb(0, 0, 0);background-color:rgb(255, 255, 255)"><a href="https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Ftwitter.com%2F&amp;data=05%7C01%7Cadmin%40tq2zr.onmicrosoft.com%7C49360182de73427cd8e908dae851e772%7C71759330a027406e9082f1f64f1007b3%7C0%7C0%7C638077735753161743%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&amp;sdata=YF3Fdvo0FyHQkXoHuhv3WzGzfhmqGjCRMdxUPIZsYvA%3D&amp;reserved=0" originalsrc="https://twitter.com/" shash="qzkaBC2sLxgP1TgKDzZQ22fgeb1b7BsI5lFHyR43eYo7m7MI1zAsITkXPZdZ6n1KIL8l5zsW9ZYym8Zh696/mItL4iYvJ0Ubwz1de7W+ONeLI4b2ew0tg4HzBWjz70b4QTUpxwi7deoO2c/HOahf1M884A1dPLtJtc8s+ZBrhcA=" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="0" style="margin:0px" class="ContentPasted0">https://twitter.com/</a></span></span>
<div class="x_elementToProof FluidPluginCopy" style="font-size:15px;font-family:&quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif;margin:0px;color:rgb(36, 36, 36);background-color:rgb(255, 255, 255)">
<span style="font-size:12pt;font-family:Calibri, Arial, Helvetica, sans-serif;margin:0px;color:rgb(0, 0, 0);background-color:rgb(255, 255, 255)"><br class="ContentPasted0">
</span></div>
<div class="x_elementToProof FluidPluginCopy" style="font-size:15px;font-family:&quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif;margin:0px;color:rgb(36, 36, 36);background-color:rgb(255, 255, 255)">
<span style="font-size:12pt;font-family:Calibri, Arial, Helvetica, sans-serif;margin:0px;color:rgb(0, 0, 0);background-color:rgb(255, 255, 255)"><a href="https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Fcarleton.ca%2F&amp;data=05%7C01%7Cadmin%40tq2zr.onmicrosoft.com%7C49360182de73427cd8e908dae851e772%7C71759330a027406e9082f1f64f1007b3%7C0%7C0%7C638077735753161743%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&amp;sdata=49SuRO9jfbmE5QmGqq85RvUZgZnyJ6XgFjlD3V7duYw%3D&amp;reserved=0" originalsrc="https://carleton.ca/" shash="Dxc62cEP1Yg+/wKXMo/VoujSwhva4+Frdv2Yr8iQuG/kuzsq8b6WfRRSuA3H0L4B+GRsbWHMjTjX4Mg2/0vuwo9UW9HOglt0hd7TcsPjzwi8IgUT3bVowbeQfPFAoMMdOWkKIzbKe4Ax/2E4rJf8j/m4b+N+/72C5VvaPLBgd+8=" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" data-safelink="true" data-linkindex="2" style="margin:0px" class="ContentPasted0">https://carleton.ca/</a></span></div>
<br>
</span></div>
<div class="elementToProof" style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);">
<span style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255);"><img style="max-width: 100%;" class="w-240 h-240" size="6492" contenttype="image/png" data-outlook-trace="F:1|T:1" src="cid:d2eb1b04-21d5-4a18-bfdb-12c4c3e65b8a"><br>
</span></div>
</body>
</html>
        """)
        self.assertEqual(0, len(embedded_urls))
    def test_get_reloaded_content_from_html_case_3(self):
        embedded_urls = ParsedEmail._get_reloaded_content_from_html(html_data="""<img class="EmojiInsert" src="data:image/gif;base64,{BASE64 emoji}" />""")
        self.assertEqual(0, len(embedded_urls))

    def url_decode(self):
        import urllib.parse
        self.assertEqual(r"data=05%7C01", urllib.parse.unquote(r"data=05|01"))