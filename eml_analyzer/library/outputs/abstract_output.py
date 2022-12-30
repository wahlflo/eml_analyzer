import abc

from eml_analyzer.library.parser.parsed_email import ParsedEmail


class AbstractOutput(abc.ABC):
    @abc.abstractmethod
    def get_final_output(self, parsed_email: ParsedEmail) -> str or None:
        pass

    @abc.abstractmethod
    def process_option_show_header(self, parsed_email: ParsedEmail) -> None:
        pass

    @abc.abstractmethod
    def process_option_show_structure(self, parsed_email: ParsedEmail) -> None:
        pass

    @abc.abstractmethod
    def process_option_show_embedded_urls_in_html(self, parsed_email: ParsedEmail) -> None:
        pass

    @abc.abstractmethod
    def process_option_show_html(self, parsed_email: ParsedEmail) -> None:
        pass

    @abc.abstractmethod
    def process_option_show_text(self, parsed_email: ParsedEmail) -> None:
        pass

    @abc.abstractmethod
    def process_option_show_attachments(self, parsed_email: ParsedEmail, extract_content: bool = False) -> None:
        pass

    @abc.abstractmethod
    def process_option_show_reloaded_content_from_html(self, parsed_email: ParsedEmail) -> None:
        pass

    def output_error_and_exit(self, exception: Exception or None, error_message: str) -> None:
        self.output_error(exception=exception, error_message=error_message)
        exit()

    @abc.abstractmethod
    def output_error(self, exception: Exception or None, error_message: str) -> None:
        pass
