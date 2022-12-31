import argparse
import io
import os
import sys
from cli_formatter.output_formatting import warning, error, info, print_headline_banner

from eml_analyzer.library.outputs import AbstractOutput, StandardOutput, JsonOutput
from eml_analyzer.library.parser import ParsedEmail, EmlParsingException, Attachment


def main():
    argument_parser = argparse.ArgumentParser(prog='emlAnalyzer', description='A CLI script to analyze an email in the EML format for viewing headers, extracting attachments, etc.')
    argument_parser.add_argument('-i', '--input', help="Path to the EML file. Accepts standard input if omitted", type=argparse.FileType('r'), nargs='?', default=sys.stdin)
    argument_parser.add_argument('--header', action='store_true', default=False, help="Shows the headers")
    argument_parser.add_argument('-x', '--tracking', action='store_true', default=False, help="Shows content which is reloaded from external resources in the HTML part")
    argument_parser.add_argument('-a', '--attachments', action='store_true', default=False, help="Lists attachments")
    argument_parser.add_argument('--text', action='store_true', default=False, help="Shows plaintext")
    argument_parser.add_argument('--html', action='store_true', default=False, help="Shows HTML")
    argument_parser.add_argument('-s', '--structure', action='store_true', default=False, help="Shows structure of the E-Mail")
    argument_parser.add_argument('-u', '--url', action='store_true', default=False, help="Shows embedded links and urls in the HTML and text part")
    argument_parser.add_argument('-ea', '--extract', type=int, default=None, help="Extracts the x-th attachment")
    argument_parser.add_argument('--extract-all', action='store_true', default=None, help="Extracts all attachments")
    argument_parser.add_argument('-o', '--output', type=str, default=None, help="Path for the extracted attachment (default is filename in working directory)")
    argument_parser.add_argument('--format', default='', const='', nargs='?', choices=['json'], help='Specifies a structured output format, the default format is not machine-readable')
    arguments = argument_parser.parse_args()

    if not arguments.input:
        warning('No input specified')
        argument_parser.print_help()
        exit()

    output_format: AbstractOutput = _get_output_from_cli_arguments_or_exit_on_error(specified_format=arguments.format)

    eml_file = _read_eml_file_or_exit_on_error(output_format=output_format, input_file=arguments.input)
    parsed_email: ParsedEmail = _parse_eml_file_or_exit_on_error(output_format=output_format, eml_content=eml_file)

    # use default functionality if no options are specified
    is_default_functionality = not (arguments.header or
                                    arguments.tracking or
                                    arguments.attachments or
                                    arguments.text or
                                    arguments.html or
                                    arguments.structure or
                                    arguments.url or
                                    arguments.extract is not None)

    if is_default_functionality:
        arguments.structure = True
        arguments.url = True
        arguments.tracking = True
        arguments.attachments = True

    if arguments.header:
        output_format.process_option_show_header(parsed_email=parsed_email)
    if arguments.structure:
        output_format.process_option_show_structure(parsed_email=parsed_email)
    if arguments.url:
        output_format.process_option_show_embedded_urls_in_html_and_text(parsed_email=parsed_email)
    if arguments.tracking:
        output_format.process_option_show_reloaded_content_from_html(parsed_email=parsed_email)
    if arguments.attachments:
        output_format.process_option_show_attachments(parsed_email=parsed_email, extract_content=arguments.extract)
    if arguments.text:
        output_format.process_option_show_text(parsed_email=parsed_email)
    if arguments.html:
        output_format.process_option_show_html(parsed_email=parsed_email)

    if arguments.extract is not None:
        if isinstance(output_format, StandardOutput):
            _extract_attachment(parsed_email=parsed_email, attachment_number=arguments.extract, output_path=arguments.output)
        else:
            output_format.output_error_and_exit(exception=None, error_message="The '--extract' argument can only be used if no output format is specified")

    if arguments.extract_all is not None and isinstance(output_format, StandardOutput):
        _extract_all_attachments(parsed_email=parsed_email, path=arguments.output)

    final_output = output_format.get_final_output(parsed_email=parsed_email)
    if final_output:
        print(final_output)


def _get_output_from_cli_arguments_or_exit_on_error(specified_format: str) -> AbstractOutput:
    if specified_format == '':
        return StandardOutput()
    elif specified_format == 'json':
        return JsonOutput()
    else:
        error('output format is not valid')
        exit()


def _read_eml_file_or_exit_on_error(output_format: AbstractOutput, input_file: io.TextIOWrapper) -> str:
    try:
        with input_file:
            return input_file.read()
    except Exception as e:
        output_format.output_error_and_exit(exception=e, error_message='File could not be loaded')


def _parse_eml_file_or_exit_on_error(output_format: AbstractOutput, eml_content: str) -> ParsedEmail:
    try:
        return ParsedEmail(eml_content=eml_content)
    except EmlParsingException as e:
        output_format.output_error_and_exit(exception=e, error_message='File could not be parsed. Sure it is an eml file?')


def _extract_attachment(parsed_email: ParsedEmail, attachment_number: int, output_path: str or None):
    print_headline_banner('Attachment Extracting')

    attachment = _get_attachment_by_index(parsed_email=parsed_email, attachment_number=attachment_number)

    # Check if attachment was found
    if attachment is None:
        error('Attachment {} could not be found'.format(attachment_number))
        return

    info('Found attachment [{}] "{}"'.format(attachment_number, attachment.filename))

    _write_attachment_to_file(attachment=attachment, output_path=output_path)


def _get_attachment_by_index(parsed_email: ParsedEmail, attachment_number: int) -> Attachment or None:
    attachments = parsed_email.get_attachments()
    for attachment in attachments:
        if attachment.index == attachment_number:
            return attachment
    return None


def _write_attachment_to_file(attachment: Attachment, output_path: str or None) -> None:
    output_path = _get_output_path_for_attachment(attachment=attachment, output_path=output_path)

    output_file = open(output_path, mode='wb')
    output_file.write(attachment.content)
    info('Attachment [{}] "{}" extracted to {}'.format(attachment.index, attachment.filename, output_path))


def _get_output_path_for_attachment(attachment: Attachment, output_path: str or None) -> str:
    if output_path is None:
        return attachment.filename
    elif os.path.isdir(output_path):
        return os.path.join(output_path, attachment.filename)


def _extract_all_attachments(parsed_email: ParsedEmail, path: str or None):
    print_headline_banner('Extracting All Attachments')

    # if no output directory is given then a default directory with the name 'eml_attachments' is used
    if path is None:
        path = 'eml_attachments'

    if not os.path.exists(path):
        os.makedirs(path)

    for attachment in parsed_email.get_attachments():
        _write_attachment_to_file(attachment=attachment, output_path=path)


if __name__ == '__main__':
    main()
