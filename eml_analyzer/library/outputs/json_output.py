import json
from typing import List

from eml_analyzer.library.outputs.abstract_output import AbstractOutput
from eml_analyzer.library.parser import ParsedEmail, Attachment, StructureItem


class JsonOutput(AbstractOutput):
    def __init__(self):
        self._result_dictionary = dict()

    def process_option_show_header(self, parsed_email: ParsedEmail) -> None:
        header_dictionary = dict()
        for key, value in parsed_email.get_header():
            if key in header_dictionary:
                header_dictionary[key].append(value)
            else:
                header_dictionary[key] = [value]
        self._result_dictionary["headers"] = header_dictionary

    def process_option_show_structure(self, parsed_email: ParsedEmail) -> None:
        structure_item = parsed_email.get_structure()
        self._result_dictionary["structure"] = JsonOutput._generate_dict_from_structure_item(structure_item=structure_item)

    @staticmethod
    def _generate_dict_from_structure_item(structure_item: StructureItem) -> dict:
        result_dict = {
            'type': structure_item.content_type,
        }

        if structure_item.filename is not None:
            result_dict['name'] = structure_item.filename
        if structure_item.content_disposition is not None:
            result_dict['disposition'] = structure_item.content_disposition

        if len(structure_item.child_items) > 0:
            child_dicts = list()
            for child in structure_item.child_items:
                child_dicts.append(JsonOutput._generate_dict_from_structure_item(structure_item=child))
            result_dict['children'] = child_dicts

        return result_dict

    def process_option_show_embedded_urls_in_html_and_text(self, parsed_email: ParsedEmail) -> None:
        self._result_dictionary["urls"] = parsed_email.get_embedded_clickable_urls_from_html_and_text()

    def process_option_show_html(self, parsed_email: ParsedEmail) -> None:
        html = parsed_email.get_html_content()
        if html is not None:
            self._result_dictionary["html"] = html

    def process_option_show_text(self, parsed_email: ParsedEmail) -> None:
        text = parsed_email.get_text_content()
        if text is not None:
            self._result_dictionary["text"] = text

    def process_option_show_attachments(self, parsed_email: ParsedEmail, extract_content: bool = False) -> None:
        attachment_list = parsed_email.get_attachments()
        self._result_dictionary["attachments"] = JsonOutput._generate_attachments_dict_from_attachment_list(attachment_list=attachment_list, extract_content=extract_content)

    @staticmethod
    def _generate_attachments_dict_from_attachment_list(attachment_list: List[Attachment], extract_content: bool) -> List[dict]:
        result_list = list()
        attachment: Attachment
        for attachment in attachment_list:
            result_list.append(JsonOutput._generate_attachment_dict_from_attachment(attachment=attachment, extract_content=extract_content))
        return result_list

    @staticmethod
    def _generate_attachment_dict_from_attachment(attachment: Attachment, extract_content: bool) -> dict:
        attachment_dict = {
            'type': attachment.content_type,
        }
        if attachment.filename is not None:
            attachment_dict['name'] = attachment.filename
        if attachment.content_disposition is not None:
            attachment_dict['disposition'] = attachment.content_disposition
        if extract_content:
            attachment_dict['content_in_base64'] = attachment.get_content_base64_encoded()
        return attachment_dict

    def process_option_show_reloaded_content_from_html(self, parsed_email: ParsedEmail) -> None:
        self._result_dictionary["reloaded_content"] = parsed_email.get_reloaded_content_from_html()

    def output_error(self, exception: Exception, error_message: str) -> None:
        error_dict = {
            'error_message': error_message,
        }
        if exception:
            error_dict['exception'] = str(exception)
        print(json.dumps(error_dict, indent=4))

    def get_final_output(self, parsed_email: ParsedEmail) -> str or None:
        error_messages: List[str] = parsed_email.get_error_messages()
        if len(error_messages) > 0:
            self._result_dictionary['warnings'] = parsed_email.get_error_messages()
        return json.dumps(self._result_dictionary, indent=4)
