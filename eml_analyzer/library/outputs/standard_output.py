from logging import warning

from cli_formatter.output_formatting import print_headline_banner, colorize_string, Color, info, error, warning

from eml_analyzer.library.outputs.abstract_output import AbstractOutput
from eml_analyzer.library.parser import ParsedEmail, StructureItem, Attachment


class StandardOutput(AbstractOutput):
    def __int__(self):
        pass

    def get_final_output(self, parsed_email: ParsedEmail) -> str or None:
        error_messages = parsed_email.get_error_messages()
        if len(error_messages) > 0:
            print()
            for message in error_messages:
                warning(message=message)
            print()
        return

    def process_option_show_header(self, parsed_email: ParsedEmail) -> None:
        print_headline_banner(headline='Header')
        max_key_width = max([len(x) for x, _ in parsed_email.get_header()])
        for key, value in parsed_email.get_header():
            values_in_lines = value.split('\n')
            first_value = values_in_lines.pop(0)
            print(colorize_string(text=key, color=Color.CYAN) + (max_key_width - len(key) + 5) * '.' + first_value)
            for x in values_in_lines:
                x = x.replace('\t', '').strip().replace('\r', '').strip(' ')
                print((max_key_width + 5) * ' ' + x)
        print()

    def process_option_show_structure(self, parsed_email: ParsedEmail) -> None:
        print_headline_banner(headline='Structure')
        structure: StructureItem = parsed_email.get_structure()
        self._print_structure(structure=structure)
        print()

    def _print_structure(self, structure: StructureItem, level: int = 0):
        filename = ('  [' + colorize_string(text=structure.filename, color=Color.CYAN) + ']') if structure.filename is not None else ''
        type_with_intend = level * '|  ' + '|- {}'.format(structure.content_type)
        print(type_with_intend.ljust(40), filename)
        for child_item in structure.child_items:
            self._print_structure(structure=child_item, level=level + 1)

    def process_option_show_embedded_urls_in_html_and_text(self, parsed_email: ParsedEmail) -> None:
        print_headline_banner(headline='URLs in HTML part')
        all_links = parsed_email.get_embedded_urls_from_html_and_text()
        if len(all_links) == 0:
            info(message='No URLs found in the html')
        for x in all_links:
            print(' - ' + colorize_string(text=x, color=Color.MAGENTA))
        print()

    def process_option_show_html(self, parsed_email: ParsedEmail) -> None:
        print_headline_banner(headline='HTML')
        html = parsed_email.get_html_content()
        if html is None:
            info('Email contains no HTML')
        else:
            print(html)
        print()

    def process_option_show_text(self, parsed_email: ParsedEmail) -> None:
        print_headline_banner(headline='Plaintext')
        text = parsed_email.get_text_content()
        if text is None:
            info('Email contains no plaintext')
        else:
            print(text)
        print()

    def process_option_show_attachments(self, parsed_email: ParsedEmail, extract_content: bool = False) -> None:
        print_headline_banner('Attachments')
        attachments_table_rows = list()
        attachment: Attachment
        for attachment in parsed_email.get_attachments():
            attachments_table_rows.append((attachment.filename, attachment.content_type, attachment.content_disposition))
        if len(attachments_table_rows) == 0:
            info('E-Mail contains no attachments')
        else:
            max_width_filename = max([len(filename) for (filename, content_type, disposition) in attachments_table_rows]) + 7
            max_width_content_type = max([len(content_type) for (filename, content_type, disposition) in attachments_table_rows]) + 7
            for index, (filename, content_type, disposition) in enumerate(attachments_table_rows):
                index_str = '[' + colorize_string(text=str(index + 1), color=Color.CYAN) + ']'
                print(index_str, filename.ljust(max_width_filename), content_type.ljust(max_width_content_type), disposition)
        print()

    def process_option_show_reloaded_content_from_html(self, parsed_email: ParsedEmail) -> None:
        print_headline_banner(headline='Reloaded Content (aka. Tracking Pixels)')
        sources = parsed_email.get_reloaded_content_from_html()
        if parsed_email.get_html_content() is None:
            warning('Email contains no HTML')
        else:
            if len(sources) == 0:
                info(message='No content found which will be reloaded from external resources')
            for x in sources:
                print(' - ' + colorize_string(text=x, color=Color.MAGENTA))
        print()

    def output_error(self, exception: Exception or None, error_message: str) -> None:
        if exception:
            error('Error: {}'.format(exception))
        error(error_message)
        info('Exiting')
