import argparse
import os
from email import message_from_string
from email.message import Message
import re
from cli_formatter.output_formatting import colorize_string, Color, warning, error, info, print_headline_banner

def show_header(parsed_eml: Message):
    print_headline_banner(headline='Header')
    max_key_width = max([len(x) for x, _ in parsed_eml.items()])
    for key, value in parsed_eml.items():
        values_in_lines = value.split('\n')
        first_value = values_in_lines.pop(0)
        print(colorize_string(text=key, color=Color.CYAN) + (max_key_width - len(key) + 5) * '.' + first_value)
        for x in values_in_lines:
            x = x.replace('\t', '').strip().replace('\r', '').strip(' ')
            print((max_key_width + 5) * ' ' + x)
    print()


def show_structure(parsed_eml: Message):
    print_headline_banner(headline='Structure')
    __show_structure(parsed_eml=parsed_eml)
    print()


def __show_structure(parsed_eml: Message, level=0):
    filename = parsed_eml.get_filename()
    filename = ('  [' + colorize_string(text=filename, color=Color.CYAN) + ']') if filename is not None else ''
    type_with_intend = level*'|  ' + '|- {}'.format(parsed_eml.get_content_type())
    print(type_with_intend.ljust(40), filename)
    if parsed_eml.is_multipart():
        for child in parsed_eml.get_payload():
            __show_structure(parsed_eml=child, level=level+1)


def check_tracking(parsed_eml: Message):
    print_headline_banner(headline='Reloaded Content (aka. Tracking Pixels)')
    sources = set()
    html_str = __get_decoded_payload(parsed_eml=parsed_eml, content_type='text/html')
    if html_str is None:
        warning('Email contains no HTML')
    else:
        for pattern in [r'src="(.+?)"', r"src='(.+?)'", r'background="(.+?)"', r"background='(.+?)'"]:
            for match in re.finditer(pattern, html_str):
                if not match.group(1).startswith('cid:'):
                    sources.add(match.group(1))
        if len(sources) == 0:
            info(message='No content found which will be reloaded from external resources')
        for x in sources:
            print(' - ' + colorize_string(text=x, color=Color.MAGENTA))
    print()


def show_urls(parsed_eml: Message):
    print_headline_banner(headline='URLs in HTML part')
    all_links = set()
    html_str = __get_decoded_payload(parsed_eml=parsed_eml, content_type='text/html')
    if html_str is None:
        warning('Email contains no HTML')
    else:
        for pattern in [r'href="(.+?)"', r"href='(.+?)'"]:
            for match in re.finditer(pattern, html_str):
                all_links.add(match.group(1))
        if len(all_links) == 0:
            info(message='No URLs found in the html')
        for x in all_links:
            print(' - ' + colorize_string(text=x, color=Color.MAGENTA))
    print()


def show_text(parsed_eml: Message):
    print_headline_banner(headline='Plaintext')
    text = __get_decoded_payload(parsed_eml=parsed_eml, content_type='text/plain')
    if text is None:
        info('Email contains no plaintext')
    else:
        print(text)
    print()


def show_html(parsed_eml: Message):
    print_headline_banner(headline='HTML')
    html = __get_decoded_payload(parsed_eml=parsed_eml, content_type='text/html')
    if html is None:
        info('Email contains no HTML')
    else:
        print(html)
    print()


def __get_decoded_payload(parsed_eml: Message, content_type: str) -> str or None:
    if parsed_eml.get_content_type() == content_type:
        html_in_bytes = parsed_eml.get_payload(decode=True)
        return __try_to_decode(content=html_in_bytes, parsed_eml=parsed_eml)
    if type(parsed_eml.get_payload()) is not list:
        return
    for sub_element in parsed_eml.get_payload():
        result = __get_decoded_payload(parsed_eml=sub_element, content_type=content_type)
        if result is not None:
            return result


def __try_to_decode(content: bytes, parsed_eml: Message) -> str or None:
    list_of_possible_encodings = __create_list_of_possible_encodings(parsed_eml=parsed_eml)

    for encoding_format in list_of_possible_encodings:
        try:
            return content.decode(encoding_format)
        except ValueError:
            continue
    error('Payload could not be decoded')
    return None


def __create_list_of_possible_encodings(parsed_eml: Message) -> set:
    """ creates a list of the most possible encodings of the payload """
    list_of_possible_encodings = set()

    # at first add the encodings mentioned in the object header
    for k, v in parsed_eml.items():
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


def show_attachments(parsed_eml: Message):
    print_headline_banner('Attachments')
    attachments = list()
    for child in parsed_eml.walk():
        if child.get_filename() is not None:
            attachments.append((child.get_filename(), str(child.get_content_type()), str(child.get_content_disposition())))
    if len(attachments) == 0:
        info('E-Mail contains no attachments')
    else:
        max_width_filename = max([len(filename) for (filename, content_type, disposition) in attachments]) + 7
        max_width_content_type = max([len(content_type) for (filename, content_type, disposition) in attachments]) + 7
        for index, (filename, content_type, disposition) in enumerate(attachments):
            index_str = '[' + colorize_string(text=str(index+1), color=Color.CYAN) + ']'
            print(index_str, filename.ljust(max_width_filename), content_type.ljust(max_width_content_type), disposition)
    print()
def extract_attachment(parsed_eml: Message, attachment_number: int, output_path: str or None):
    print_headline_banner('Attachment Extracting')
    attachment = None
    counter = 1
    for child in parsed_eml.walk():
        if child.get_filename() is not None:
            if counter == attachment_number:
                attachment = child
                break
            counter += 1

    # Check if attachment was found
    if attachment is None:
        error('Attachment {} could not be found'.format(attachment_number))
        return

    info('Found attachment [{}] "{}"'.format(attachment_number, attachment.get_filename()))

    if output_path is None:
        output_path = attachment.get_filename()
    elif os.path.isdir(output_path):
        output_path = os.path.join(output_path, attachment.get_filename())

    payload = attachment.get_payload(decode=True)
    output_file = open(output_path, mode='wb')
    output_file.write(payload)
    info('Attachment extracted to {}'.format(output_path))
    
def extract_all_attachments(parsed_eml: Message, output_path: str or None):
    print_headline_banner('Attachment Extracting')
    attachment = None
    for child in parsed_eml.walk():
      if child.get_filename() is None:
        continue
      print(child.get_filename())
      path = output_path
      attachment = child      
      if path is None:
          path = attachment.get_filename()
      elif os.path.isdir(path):
          path = os.path.join(path, attachment.get_filename())
      payload = attachment.get_payload(decode=True)
      output_file = open(path, mode='wb')
      output_file.write(payload)
      info('Attachment extracted to {}'.format(path))
    
def main():
    argument_parser = argparse.ArgumentParser(usage='emlAnalyzer [OPTION]... [FILE]', description='A cli script to analyze an E-Mail in the eml format for viewing the header, extracting attachments etc.')
    argument_parser.add_argument('-i', '--input', help="path to the eml-file (is required)", type=str)
    argument_parser.add_argument('--header', action='store_true', default=False, help="Shows the headers")
    argument_parser.add_argument('-x', '--tracking', action='store_true', default=False, help="Shows content which is reloaded from external ressources in the HTML part")
    argument_parser.add_argument('-a', '--attachments', action='store_true', default=False, help="Lists attachments")
    argument_parser.add_argument('--text', action='store_true', default=False, help="Shows plaintext")
    argument_parser.add_argument('--html', action='store_true', default=False, help="Shows HTML")
    argument_parser.add_argument('-s', '--structure', action='store_true', default=False, help="Shows structure of the E-Mail")
    argument_parser.add_argument('-u', '--url', action='store_true', default=False, help="Shows embedded links and urls in the html part")
    argument_parser.add_argument('-ea', '--extract', type=int, default=None, help="Extracts the x-th attachment")
    argument_parser.add_argument('--extract-all', action='store_true', default=None, help="Extracts all attachments")
    argument_parser.add_argument('-o', '--output', type=str, default=None, help="Path for the extracted attachment (default is filename in working directory)")
    arguments = argument_parser.parse_args()

    if arguments.input is None or len(arguments.input) == 0:
        warning('No Input specified')
        argument_parser.print_help()
        exit()

    # get the absolute path to the input file
    path_to_input = os.path.abspath(arguments.input)

    # read the eml file
    try:
        with open(path_to_input, mode='r') as input_file:
            eml_content = input_file.read()
    except Exception as e:
        error('Error: {}'.format(e))
        error('File could not be loaded')
        info('Existing')
        exit()

    # parse the eml file
    try:
        parsed_eml = message_from_string(eml_content)
    except Exception as e:
        error('Error: {}'.format(e))
        error('File could not be parsed. Sure it is a eml-file?')
        info('Existing')
        exit()

    # use default functionality if no options are specified
    is_default_functionality = not (arguments.header or
                                    arguments.tracking or
                                    arguments.attachments or
                                    arguments.text or
                                    arguments.html or
                                    arguments.structure or
                                    arguments.url or
                                    arguments.extract or
                                    arguments.extract_all is not None)

    if is_default_functionality:
        arguments.structure = True
        arguments.url = True
        arguments.tracking = True
        arguments.attachments = True

    if arguments.header:
        show_header(parsed_eml=parsed_eml)
    if arguments.structure:
        show_structure(parsed_eml=parsed_eml)
    if arguments.url:
        show_urls(parsed_eml=parsed_eml)
    if arguments.tracking:
        check_tracking(parsed_eml=parsed_eml)
    if arguments.attachments:
        show_attachments(parsed_eml=parsed_eml)
    if arguments.text:
        show_text(parsed_eml=parsed_eml)
    if arguments.html:
        show_html(parsed_eml=parsed_eml)
    if arguments.extract is not None:
        extract_attachment(parsed_eml=parsed_eml, attachment_number=arguments.extract, output_path=arguments.output)
    if arguments.extract_all is not None:
        extract_all_attachments(parsed_eml=parsed_eml, output_path=arguments.output)


if __name__ == '__main__':
    main()
