#
# Copyright 2024 Tabs Data Inc.
#

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from tabsdatasdk.exceptions import ErrorCode, FormatConfigurationError

CSV_EXTENSION = "csv"
JSON_LINES_EXTENSION = "jsonl"
LOG_EXTENSION = "log"
NDJSON_EXTENSION = "ndjson"
PARQUET_EXTENSION = "parquet"


class FileFormat(ABC):
    """The class of the different possible formats for files."""

    IDENTIFIER = None

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Returns the dictionary representation of the object.

        Returns:
            dict: A dictionary with the object's attributes.
        """

    def __eq__(self, other: object) -> bool:
        """
        Compares a FileFormat with another object.

        Args:
            other: The other object to compare.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if not isinstance(other, FileFormat):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        """
        Returns a string representation of the FileInput.

        Returns:
            str: A string representation of the FileInput.
        """
        return f"{self.__class__.__name__}({self.to_dict()[self.IDENTIFIER]})"


class FileFormatIdentifier(Enum):
    """
    Enum for the identifiers of the different types of data outputs.
    """

    CSV = "csv-format"
    LOG = "log-format"
    NDJSON = "ndjson-format"
    PARQUET = "parquet-format"


class CSVFormat(FileFormat):
    """The class of the CSV file format.

    Attributes:
        separator (str | int): The separator of the CSV file.
        quote_char (str | int): The quote character of the CSV file.
        eol_char (str | int): The end of line character of the CSV file.
        encoding (str): The encoding of the CSV file.
        null_values (list | None): The null values of the CSV file.
        missing_is_null (bool): Whether missing values should be marked as null.
        truncate_ragged_lines (bool): Whether to truncate ragged lines of the CSV file.
        comment_prefix (str | int | None): The comment prefix of the CSV file.
        try_parse_dates (bool): Whether to try parse dates of the CSV file.
        decimal_comma (bool): Whether the CSV file uses decimal comma.
        has_header (bool): If the CSV file has header.
        skip_rows (int): How many rows should be skipped in the CSV file.
        skip_rows_after_header (int): How many rows should be skipped after the
            header in the CSV file.
        raise_if_empty (bool): If an error should be raised for an empty CSV.
        ignore_errors (bool): If the errors loading the CSV must be ignored.
    """

    IDENTIFIER = FileFormatIdentifier.CSV.value

    DEFAULT_SEPARATOR = ","
    DEFAULT_QUOTE_CHAR = '"'
    DEFAULT_EOL_CHAR = "\n"
    DEFAULT_ENCODING = "Utf8"
    DEFAULT_NULL_VALUES = None
    DEFAULT_MISSING_IS_NULL = True
    DEFAULT_TRUNCATE_RAGGED_LINES = False
    DEFAULT_COMMENT_PREFIX = None
    DEFAULT_TRY_PARSE_DATES = False
    DEFAULT_DECIMAL_COMMA = False
    DEFAULT_HAS_HEADER = True
    DEFAULT_SKIP_ROWS = 0
    DEFAULT_SKIP_ROWS_AFTER_HEADER = 0
    DEFAULT_RAISE_IF_EMPTY = True
    DEFAULT_IGNORE_ERRORS = False

    def __init__(
        self,
        separator: str | int = DEFAULT_SEPARATOR,
        quote_char: str | int = DEFAULT_QUOTE_CHAR,
        eol_char: str | int = DEFAULT_EOL_CHAR,
        encoding: str = DEFAULT_ENCODING,
        null_values: list | None = DEFAULT_NULL_VALUES,
        missing_is_null: bool = DEFAULT_MISSING_IS_NULL,
        truncate_ragged_lines: bool = DEFAULT_TRUNCATE_RAGGED_LINES,
        comment_prefix: str | int | None = DEFAULT_COMMENT_PREFIX,
        try_parse_dates: bool = DEFAULT_TRY_PARSE_DATES,
        decimal_comma: bool = DEFAULT_DECIMAL_COMMA,
        has_header: bool = DEFAULT_HAS_HEADER,
        skip_rows: int = DEFAULT_SKIP_ROWS,
        skip_rows_after_header: int = DEFAULT_SKIP_ROWS_AFTER_HEADER,
        raise_if_empty: bool = DEFAULT_RAISE_IF_EMPTY,
        ignore_errors: bool = DEFAULT_IGNORE_ERRORS,
    ):
        """
        Initializes the CSV format object.

        Args:
            separator (str | int, optional): The separator of the CSV file.
            quote_char (str | int, optional): The quote character of the CSV file.
            eol_char (str | int, optional): The end of line character of the CSV file.
            encoding (str, optional): The encoding of the CSV file.
            null_values (list | None, optional): The null values of the CSV file.
            missing_is_null (bool, optional): Whether missing values should be marked
                as null.
            truncate_ragged_lines (bool, optional): Whether to truncate ragged lines
                of the CSV file.
            comment_prefix (str | int | None, optional): The comment prefix of the CSV
                file.
            try_parse_dates (bool, optional): Whether to try parse dates of the CSV
                file.
            decimal_comma (bool, optional): Whether the CSV file uses decimal comma.
            has_header (bool, optional): If the CSV file has header.
            skip_rows (int, optional): How many rows should be skipped in the CSV file.
            skip_rows_after_header (int, optional): How many rows should be skipped
                after the header in the CSV file.
            raise_if_empty (bool, optional): If an error should be raised for an empty
                CSV.
            ignore_errors (bool, optional): If the errors loading the CSV must be
                ignored.
        """
        self.separator = _verify_type_or_raise_exception(
            separator, (str, int), "separator", self.__class__.__name__
        )
        self.quote_char = _verify_type_or_raise_exception(
            quote_char, (str, int), "quote_char", self.__class__.__name__
        )
        self.eol_char = _verify_type_or_raise_exception(
            eol_char, (str, int), "eol_char", self.__class__.__name__
        )
        self.encoding = _verify_type_or_raise_exception(
            encoding, (str,), "encoding", self.__class__.__name__
        )
        self.null_values = _verify_type_or_raise_exception(
            null_values, (list, None), "null_values", self.__class__.__name__
        )
        self.missing_is_null = _verify_type_or_raise_exception(
            missing_is_null, (bool,), "missing_is_null", self.__class__.__name__
        )
        self.truncate_ragged_lines = _verify_type_or_raise_exception(
            truncate_ragged_lines,
            (bool,),
            "truncate_ragged_lines",
            self.__class__.__name__,
        )
        self.comment_prefix = _verify_type_or_raise_exception(
            comment_prefix, (str, int, None), "comment_prefix", self.__class__.__name__
        )
        self.try_parse_dates = _verify_type_or_raise_exception(
            try_parse_dates, (bool,), "try_parse_dates", self.__class__.__name__
        )
        self.decimal_comma = _verify_type_or_raise_exception(
            decimal_comma, (bool,), "decimal_comma", self.__class__.__name__
        )
        self.has_header = _verify_type_or_raise_exception(
            has_header, (bool,), "has_header", self.__class__.__name__
        )
        self.skip_rows = _verify_type_or_raise_exception(
            skip_rows, (int,), "skip_rows", self.__class__.__name__
        )
        self.skip_rows_after_header = _verify_type_or_raise_exception(
            skip_rows_after_header,
            (int,),
            "skip_rows_after_header",
            self.__class__.__name__,
        )
        self.raise_if_empty = _verify_type_or_raise_exception(
            raise_if_empty, (bool,), "raise_if_empty", self.__class__.__name__
        )
        self.ignore_errors = _verify_type_or_raise_exception(
            ignore_errors, (bool,), "ignore_errors", self.__class__.__name__
        )

    def to_dict(self) -> dict:
        """
        Returns the dictionary representation of the object.

        Returns:
            dict: A dictionary with the object's attributes.
        """
        return {
            self.IDENTIFIER: {
                "separator": self.separator,
                "quote_char": self.quote_char,
                "eol_char": self.eol_char,
                "encoding": self.encoding,
                "null_values": self.null_values,
                "missing_is_null": self.missing_is_null,
                "truncate_ragged_lines": self.truncate_ragged_lines,
                "comment_prefix": self.comment_prefix,
                "try_parse_dates": self.try_parse_dates,
                "decimal_comma": self.decimal_comma,
                "has_header": self.has_header,
                "skip_rows": self.skip_rows,
                "skip_rows_after_header": self.skip_rows_after_header,
                "raise_if_empty": self.raise_if_empty,
                "ignore_errors": self.ignore_errors,
            },
        }


class NDJSONFormat(FileFormat):
    """The class of the log file format."""

    IDENTIFIER = FileFormatIdentifier.NDJSON.value

    def to_dict(self) -> dict:
        """
        Returns the dictionary representation of the object.

        Returns:
            dict: A dictionary with the object's attributes.
        """
        return {self.IDENTIFIER: {}}


class LogFormat(FileFormat):
    """The class of the log file format."""

    IDENTIFIER = FileFormatIdentifier.LOG.value

    def to_dict(self) -> dict:
        """
        Returns the dictionary representation of the object.

        Returns:
            dict: A dictionary with the object's attributes.
        """
        return {self.IDENTIFIER: {}}


class ParquetFormat(FileFormat):
    """The class of the Parquet file format."""

    IDENTIFIER = FileFormatIdentifier.PARQUET.value

    def to_dict(self) -> dict:
        """
        Returns the dictionary representation of the object.

        Returns:
            dict: A dictionary with the object's attributes.
        """
        return {self.IDENTIFIER: {}}


def _verify_type_or_raise_exception(value, tuple_of_types, variable_name, class_name):
    if None in tuple_of_types and value is None:
        return None
    else:
        tuple_of_types = tuple(x for x in tuple_of_types if x is not None)

    if not isinstance(value, tuple_of_types):
        raise FormatConfigurationError(
            ErrorCode.FOCE3, variable_name, class_name, tuple_of_types, type(value)
        )
    if isinstance(value, bool) and bool not in tuple_of_types:
        raise FormatConfigurationError(
            ErrorCode.FOCE3, variable_name, class_name, tuple_of_types, type(value)
        )
    return value


STR_TO_FILE_FORMAT = {
    CSV_EXTENSION: CSVFormat,
    JSON_LINES_EXTENSION: NDJSONFormat,
    LOG_EXTENSION: LogFormat,
    NDJSON_EXTENSION: NDJSONFormat,
    PARQUET_EXTENSION: ParquetFormat,
}


def build_file_format(configuration: dict | str | FileFormat) -> FileFormat:
    """
    Builds a file format object from a dictionary, a string or a Format Object.
    :return: A file format object.
    """
    if isinstance(configuration, FileFormat):
        return configuration
    elif isinstance(configuration, str):
        if configuration not in STR_TO_FILE_FORMAT:
            raise FormatConfigurationError(
                ErrorCode.FOCE4,
                configuration,
                [element for element in STR_TO_FILE_FORMAT],
            )
        return STR_TO_FILE_FORMAT[configuration]()
    elif isinstance(configuration, dict):
        return build_file_format_from_dict(configuration)
    elif configuration is None:
        raise FormatConfigurationError(ErrorCode.FOCE6, [dict, str, FileFormat])
    else:
        raise FormatConfigurationError(
            ErrorCode.FOCE5, [dict, str, FileFormat], type(configuration)
        )


def build_file_format_from_dict(configuration: dict) -> FileFormat:
    valid_identifiers = [element.value for element in FileFormatIdentifier]
    # The input dictionary must have exactly one key, which must be one of the
    # valid identifiers
    if len(configuration) != 1 or next(iter(configuration)) not in valid_identifiers:
        raise FormatConfigurationError(
            ErrorCode.FOCE1, valid_identifiers, list(configuration.keys())
        )
    # Since we have only one key, we select the identifier and the configuration
    identifier, format_configuration = next(iter(configuration.items()))
    # The configuration must be a dictionary
    if not isinstance(format_configuration, dict):
        raise FormatConfigurationError(
            ErrorCode.FOCE2, identifier, type(format_configuration)
        )
    if identifier == FileFormatIdentifier.CSV.value:
        return CSVFormat(**format_configuration)
    elif identifier == FileFormatIdentifier.LOG.value:
        return LogFormat()
    elif identifier == FileFormatIdentifier.PARQUET.value:
        return ParquetFormat()
    elif identifier == FileFormatIdentifier.NDJSON.value:
        return NDJSONFormat()


def get_implicit_format_from_list(path_list: list) -> str:
    # Our current logic is to infer the format from the file extension of the data
    # if it is not provided. We will use the first file extension in the list of
    # paths. To find it, we take the first value after a '.' in the path. If there
    # is no '.' in the path, the format will remain as None
    implicit_format = None
    for path_str in path_list:
        path = Path(path_str)
        if path.suffix:
            implicit_format = path.suffix[1:]  # Remove the leading dot
            break
    return implicit_format
