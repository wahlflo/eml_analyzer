import re
import email
import email.message
import urllib.parse
import html
import warnings
from typing import NamedTuple, List, Tuple, Set

from eml_analyzer.library.parser.attachment import Attachment
from eml_analyzer.library.parser.structure_item import StructureItem


class EmlParsingException(Exception):
    pass


class PayloadDecodingException(Exception):
    pass


class FoundUrl(NamedTuple):
    url: str
    original: str


class ParsedEmail:
    def __init__(self, eml_content: str):
        self._parsed_email = ParsedEmail._parse_email(eml_content=eml_content)

        self._html_was_analyzed: bool = False
        self._html_content: str or None = None

        # an list containing error messages which occurred during parsing
        self._error_messages: List[str] = list()

    @staticmethod
    def _parse_email(eml_content: str) -> email.message.Message:
        try:
            return email.message_from_string(eml_content)
        except Exception as e:
            raise EmlParsingException(e)

    def get_error_messages(self) -> List[str]:
        return self._error_messages

    def _add_error_messages(self, error_message: str) -> None:
        self._error_messages.append(error_message)

    def get_header(self) -> List[Tuple[str, any]]:
        """ returns list of key-value pairs of header entries """
        return self._parsed_email.items()

    def get_structure(self) -> StructureItem:
        return StructureItem(message=self._parsed_email)

    def get_text_content(self) -> str or None:
        return self._get_decoded_payload_with_first_matching_type(content_type='text/plain')

    def get_html_content(self) -> str or None:
        # check if the html was already extracted in the past to prevent double work
        if not self._html_was_analyzed:
            self._html_content = self._get_decoded_payload_with_first_matching_type(content_type='text/html')
        return self._html_content

    def _get_decoded_payload_with_first_matching_type(self, content_type: str) -> str or None:
        first_matched_payload = ParsedEmail._get_first_email_payload_with_matching_type(message=self._parsed_email, content_type=content_type)
        if first_matched_payload is not None:
            try:
                return ParsedEmail._get_decoded_payload_from_message(message=first_matched_payload)
            except PayloadDecodingException:
                self._add_error_messages(error_message='Payload with the type "{}" could not be decoded'.format(content_type))
        return None

    @staticmethod
    def _get_first_email_payload_with_matching_type(message: email.message.Message, content_type: str) -> email.message.Message or None:
        if message.get_content_type() == content_type:
            return message

        child_payloads = message.get_payload()
        if type(child_payloads) is list:
            for child_payload in child_payloads:
                found_payload = ParsedEmail._get_first_email_payload_with_matching_type(message=child_payload, content_type=content_type)
                if found_payload is not None:
                    return found_payload
        return None

    @staticmethod
    def _get_decoded_payload_from_message(message: email.message.Message) -> None or str:
        payload_in_bytes = message.get_payload(decode=True)

        list_of_possible_encodings = ParsedEmail._create_list_of_possible_encodings(message=message)

        for encoding_format in list_of_possible_encodings:
            try:
                return payload_in_bytes.decode(encoding_format)
            except ValueError:
                continue
        raise PayloadDecodingException('Payload could not be decoded')

    @staticmethod
    def _create_list_of_possible_encodings(message: email.message.Message) -> set:
        """ creates a list of the most possible encodings of a payload """
        list_of_possible_encodings = set()

        # at first add the encodings mentioned in the object header
        for k, v in message.items():
            k = str(k).lower()
            v = str(v).lower()
            if k == 'content-type':
                entries = v.split(';')
                for entry in entries:
                    entry = entry.strip()
                    if entry.startswith('charset='):
                        encoding = entry.replace('charset=', '').replace('"', '')
                        list_of_possible_encodings.add(encoding)

        for x in ['utf-8', 'windows-1251', 'iso-8859-1', 'us-ascii', 'iso-8859-15']:
            if x not in list_of_possible_encodings:
                list_of_possible_encodings.add(x)

        return list_of_possible_encodings

    def get_attachments(self) -> List[Attachment]:
        return_list = list()
        counter = 0
        for child in self._parsed_email.walk():
            if child.get_filename() is not None:
                counter += 1
                return_list.append(Attachment(message=child, index=counter))
        return return_list

    def get_embedded_urls_from_html_and_text(self) -> List[str]:
        warnings.warn(
            "get_embedded_urls_from_html_and_text is deprecated, use get_embedded_clickable_urls_from_html_and_text instead",
            DeprecationWarning
        )
        return self.get_embedded_clickable_urls_from_html_and_text()

    def get_embedded_clickable_urls_from_html_and_text(self) -> List[str]:
        found_urls = set()
        html_data: str or None = self.get_html_content()
        if html_data is not None:
            found_urls.update(ParsedEmail._get_embedded_clickable_urls_from_html(html_data=html_data))
        text: str or None = self.get_text_content()
        if text is not None:
            found_urls.update(ParsedEmail._get_embedded_urls_from_text(text=text))
        return list(found_urls)

    @staticmethod
    def _get_embedded_clickable_urls_from_html(html_data: str) -> Set[str]:
        # find urls which are referenced in html links
        found_urls_in_html_links = ParsedEmail._get_embedded_clickable_urls_from_html_links(html_data=html_data)
        found_urls_in_html_text = ParsedEmail._get_embedded_clickable_urls_from_html_text(html_data=html_data, found_urls=found_urls_in_html_links)

        found_urls = found_urls_in_html_text
        found_url: FoundUrl
        for found_url in found_urls_in_html_links:
            found_urls.add(found_url.url)
        return found_urls

    @staticmethod
    def _get_embedded_clickable_urls_from_html_links(html_data: str) -> [FoundUrl]:
        """ extracts URLs from HTML links """
        found_urls = list()
        for pattern_template in [r' href="(.+?)"', r" href='(.+?)'", r" originalsrc='(.+?)'", r' originalsrc="(.+?)"']:
            pattern = re.compile(pattern_template, re.IGNORECASE)
            for match in re.finditer(pattern, html_data):
                extracted_url = match.group(1)
                decoded_url = html.unescape(extracted_url)
                decoded_url = urllib.parse.unquote(decoded_url)
                found_url = FoundUrl(decoded_url, extracted_url)
                found_urls.append(found_url)
        return found_urls

    @staticmethod
    def _get_embedded_clickable_urls_from_html_text(html_data: str, found_urls: [FoundUrl]) -> Set[str]:
        """ extracts URLs from HTML to capture also URLs which are embedded into the text rendered by the HTML payload """
        # remove at first the reloaded content from the html to prevent that URL from reloaded content are added to the embedded clickable URLs
        html_data = ParsedEmail._get_new_html_without_reloaded_content(html_data=html_data)
        # then remove the already found URLs
        found_url: FoundUrl
        for found_url in found_urls:
            html_data = html_data.replace(found_url.original, '')

        return ParsedEmail._get_embedded_urls_from_text(text=html_data)

    @staticmethod
    def _get_embedded_urls_from_text(text: str) -> Set[str]:
        found_urls = set()
        pattern = re.compile(r'(http|https|ftp|ftps)\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?', re.IGNORECASE)
        for match in re.finditer(pattern, text):
            found_urls.add(match.group(0))
        return found_urls

    def get_reloaded_content_from_html(self) -> List[str]:
        html_data: str or None = self.get_html_content()
        if html_data is not None:
            return ParsedEmail._get_reloaded_content_from_html(html_data=html_data)
        return list()

    @staticmethod
    def _get_reloaded_content_from_html(html_data: str) -> List[str]:
        sources = list()
        for pattern_template in ParsedEmail._get_patterns_for_reloaded_content():
            pattern = re.compile(pattern_template, re.IGNORECASE)
            for match in re.finditer(pattern, html_data):
                extracted_url = match.group(1)
                # embedded items which are attached to the email as attachment are referred to with a staring 'cid:', so these will be ignored
                if not extracted_url.startswith('cid:') and not extracted_url.startswith('data:'):
                    # decode URL
                    decoded_url: str = urllib.parse.unquote(extracted_url)
                    sources.append(decoded_url)
        return sources

    @staticmethod
    def _get_new_html_without_reloaded_content(html_data: str) -> str:
        for pattern_template in ParsedEmail._get_patterns_for_reloaded_content():
            pattern = re.compile(pattern_template, re.IGNORECASE)
            for match in re.finditer(pattern, html_data):
                html_data = html_data.replace(match.group(0), '')
        return html_data

    @staticmethod
    def _get_patterns_for_reloaded_content() -> List[str]:
        return [r' src="(.+?)"', r" src='(.+?)'", r' background="(.+?)"', r" background='(.+?)'"]
