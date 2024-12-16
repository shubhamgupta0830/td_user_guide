#
# Copyright 2024 Tabs Data Inc.
#

import datetime
import inspect
import logging
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List
from urllib.parse import urlparse, urlunparse

from tabsdatasdk.credentials import (
    AzureCredentials,
    S3Credentials,
    UserPasswordCredentials,
    build_credentials,
)
from tabsdatasdk.exceptions import (
    ErrorCode,
    FunctionConfigurationError,
    InputConfigurationError,
    OutputConfigurationError,
)
from tabsdatasdk.format import (
    CSVFormat,
    FileFormat,
    LogFormat,
    NDJSONFormat,
    ParquetFormat,
    build_file_format,
    get_implicit_format_from_list,
)
from tabsdatasdk.plugin import InputPlugin, OutputPlugin
from tabsdatasdk.uri import URI, URI_INDICATOR, build_uri_object

logger = logging.getLogger(__name__)

TABLES_KEY = "tables"

AZURE_SCHEME = "az"
FILE_SCHEME = "file"
MYSQL_SCHEME = "mysql"
S3_SCHEME = "s3"


class InputIdentifiers(Enum):
    """
    Enum for the identifiers of the different types of data inputs.
    """

    AZURE = "azure-input"
    LOCALFILE = "localfile-input"
    MYSQL = "mysql-input"
    S3 = "s3-input"
    TABLE = "table-input"


class OutputIdentifiers(Enum):
    """
    Enum for the identifiers of the different types of data outputs.
    """

    MYSQL = "mysql-output"
    TABLE = "table-output"


class Input(ABC):
    """
    Abstract base class for managing data input configurations.
    """

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert the Input object to a dictionary with all
            the relevant information.

        Returns:
            dict: A dictionary with the relevant information of the Input
                object.
        """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Input):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Input.

        Returns:
            str: A string representation of the Input.
        """
        return f"{self.__class__.__name__}({self.to_dict()[self.IDENTIFIER]})"


class AzureInput(Input):
    """
    Class for managing the configuration of Azure-file-based data inputs.

    Attributes:
        format (FileFormat): The format of the file. If not provided, it will be
            inferred from the file extension of the data.
        uri (str | List[str]): The URI of the files with format: 'az://path/to/files'.
            It can be a single URI or a list of URIs.
        credentials (AzureCredentials): The credentials required to access Azure.
        initial_last_modified (str | datetime.datetime): If provided, only the files
            modified after this date and time will be considered.

    Methods:
        to_dict(): Converts the S3Input object to a dictionary.
    """

    IDENTIFIER = InputIdentifiers.AZURE.value

    CREDENTIALS_KEY = "credentials"
    FORMAT_KEY = "format"
    LAST_MODIFIED_KEY = "initial_last_modified"
    URI_KEY = "uri"

    class SupportedFormats(Enum):
        """
        Enum for the supported formats for the S3Input.
        """

        csv = CSVFormat
        json = NDJSONFormat
        log = LogFormat
        parquet = ParquetFormat

    def __init__(
        self,
        uri: str | List[str],
        credentials: dict | AzureCredentials,
        format: str | dict | FileFormat = None,
        initial_last_modified: str | datetime.datetime = None,
    ):
        """
        Initializes the AzureInput with the given URI and the credentials required to
            access Azure, and optionally a format and date and
            time after which the files were modified.

        Args:
            uri (str | List[str]): The URI of the files with format:
                'az://path/to/files'. It can be a single URI or a list of URIs.
            credentials (dict | AzureCredentials): The credentials required to access
                Azure. Can be a dictionary or a AzureCredentials object.
            format (str | dict | FileFormat, optional): The format of the file. If not
                provided, it will be inferred from the file extension of the data.
                Can be either a string with the format, a FileFormat object or a
                dictionary with the format as the 'type' key and any additional
                format-specific information. Currently supported formats are 'csv',
                'parquet', 'ndjson', 'jsonl' and 'log'.
            initial_last_modified (str | datetime.datetime, optional): If provided,
                only the files modified after this date and time will be considered.
                The date and time can be provided as a string in
                [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) or as
                a datetime object. If no timezone is provided, UTC will be assumed.

        Raises:
            InputConfigurationError
            FormatConfigurationError
        """
        self.uri = uri
        self.format = format
        self.initial_last_modified = initial_last_modified
        self.credentials = credentials

    @property
    def uri(self) -> str | List[str]:
        """
        str | List[str]: The URI of the files with format: 'az://path/to/files'.
        """
        return self._uri

    @uri.setter
    def uri(self, uri: str | List[str]):
        """
        Sets the URI of the files with format: 'az://path/to/files'.

        Args:
            uri (str | List[str]): The URI of the files with format:
                'az://path/to/files'. It can be a single URI or a list of URIs.
        """
        self._uri = uri
        if isinstance(uri, str):
            self._uri_list = [uri]
        elif isinstance(uri, list):
            self._uri_list = uri
            if not all(isinstance(single_uri, str) for single_uri in self._uri_list):
                raise InputConfigurationError(ErrorCode.ICE28, type(uri))
        else:
            raise InputConfigurationError(ErrorCode.ICE28, type(uri))

        self._parsed_uri_list = [urlparse(single_uri) for single_uri in self._uri_list]
        for parsed_uri in self._parsed_uri_list:
            if parsed_uri.scheme != AZURE_SCHEME:
                raise InputConfigurationError(
                    ErrorCode.ICE29,
                    parsed_uri.scheme,
                    AZURE_SCHEME,
                    urlunparse(parsed_uri),
                )

        self._implicit_format = get_implicit_format_from_list(self._uri_list)
        if hasattr(self, "_format") and self._format is None:
            self._verify_valid_format(build_file_format(self._implicit_format))

    def to_dict(self) -> dict:
        """
        Converts the AzureInput object to a dictionary with all the relevant
            information.

        Returns:
            dict: A dictionary with the relevant information of the AzureInput
                object: URI, format, credentials and last_modified time.
        """
        return {
            self.IDENTIFIER: {
                self.FORMAT_KEY: self.format.to_dict(),
                self.LAST_MODIFIED_KEY: self.initial_last_modified,
                self.URI_KEY: self._uri_list,
                self.CREDENTIALS_KEY: self.credentials.to_dict(),
            }
        }

    @property
    def format(self) -> FileFormat:
        """
        FileFormat: The format of the file. If not provided, it will be inferred from
            the file extension of the data.
        """
        return self._format or build_file_format(self._implicit_format)

    @format.setter
    def format(self, format: str | dict | FileFormat):
        """
        Sets the format of the file.

        Args:
            format (str | dict | FileFormat): The format of the file. If not
                provided, it will be inferred from the file extension of the data.
                Can be either a string with the format, a FileFormat object or a
                dictionary with the format as the 'type' key and any additional
                format-specific information. Currently supported formats are 'csv',
                'parquet', 'ndjson', 'jsonl' and 'log'.
        """
        if format is None:
            self._format = None
            # No format was provided, so we validate that self._implicit_format is valid
            self._verify_valid_format(build_file_format(self._implicit_format))
        else:
            format = build_file_format(format)
            self._verify_valid_format(format)
            self._format = format

    def _verify_valid_format(self, format: FileFormat):
        """
        Verifies that the provided format is valid for the S3Input

        Args:
            format (FileFormat): The format to verify.
        """
        valid_input_formats = tuple(element.value for element in self.SupportedFormats)
        if not (isinstance(format, valid_input_formats)):
            raise InputConfigurationError(
                ErrorCode.ICE4, type(format), valid_input_formats
            )

    @property
    def initial_last_modified(self) -> str:
        """
        str: The date and time after which the files were modified.
        """
        return (
            self._initial_last_modified.isoformat(timespec="microseconds")
            if self._initial_last_modified
            else None
        )

    @initial_last_modified.setter
    def initial_last_modified(self, initial_last_modified: str | datetime.datetime):
        """
        Sets the date and time after which the files were modified.

        Args:
            initial_last_modified (str | datetime.datetime): The date and time after
                which the files were modified. The date and time can be provided as a
                string in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601)
                or as a datetime object. If no timezone is
                provided, UTC will be assumed.
        """
        if initial_last_modified:
            if isinstance(initial_last_modified, datetime.datetime):
                self._initial_last_modified = initial_last_modified
            else:
                try:
                    self._initial_last_modified = datetime.datetime.fromisoformat(
                        initial_last_modified
                    )
                except ValueError:
                    raise InputConfigurationError(ErrorCode.ICE5, initial_last_modified)
                except TypeError:
                    raise InputConfigurationError(
                        ErrorCode.ICE6, type(initial_last_modified)
                    )
        else:
            self._initial_last_modified = None

    @property
    def credentials(self) -> AzureCredentials:
        """
        AzureCredentials: The credentials required to access Azure.
        """
        return self._credentials

    @credentials.setter
    def credentials(self, credentials: dict | AzureCredentials):
        """
        Sets the credentials required to access Azure.

        Args:
            credentials (dict | AzureCredentials): The credentials required to access
                Azure. Can be a dictionary or an AzureCredentials object.
        """
        credentials = build_credentials(credentials)
        if not (isinstance(credentials, AzureCredentials)):
            raise InputConfigurationError(ErrorCode.ICE20, type(credentials))
        self._credentials = credentials


class LocalFileInput(Input):
    """
    Class for managing the configuration of local-file-based data inputs.

    Attributes:
        format (FileFormat): The format of the file. If not provided, it will be
            inferred from the file extension of the data.
        path (str | List[str]): The path where the files can be found. It can be a
            single path or a list of paths.
        initial_last_modified (str | None): If not None, only the files modified after
            this date and time will be considered.

    Methods:
        to_dict(): Converts the LocalFileInput object to a dictionary.
    """

    IDENTIFIER = InputIdentifiers.LOCALFILE.value

    FORMAT_KEY = "format"
    LAST_MODIFIED_KEY = "initial_last_modified"
    PATH_KEY = "path"

    class SupportedFormats(Enum):
        """
        Enum for the supported formats for the LocalFileInput.
        """

        csv = CSVFormat
        json = NDJSONFormat
        log = LogFormat
        parquet = ParquetFormat

    def __init__(
        self,
        path: str | List[str],
        format: str | dict | FileFormat = None,
        initial_last_modified: str | datetime.datetime = None,
    ):
        """
        Initializes the LocalFileInput with the given path, and optionally a format and
            a date and time after which the files were modified.

        Args:
            path (str | List[str]): The path where the files can be found. It can be a
                single path or a list of paths.
            format (str | dict | FileFormat, optional): The format of the file. If not
                provided, it will be inferred from the file extension of the data.
                Can be either a string with the format, a FileFormat object or a
                dictionary with the format as the 'type' key and any additional
                format-specific information. Currently supported formats are 'csv',
                'parquet', 'json', and 'log'.
            initial_last_modified (str | datetime.datetime, optional): If provided,
                only the files modified after this date and time will be considered.
                The date and time can be provided as a string in
                [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) or as
                a datetime object. If no timezone is provided, UTC will be assumed.

        Raises:
            InputConfigurationError
            FormatConfigurationError
        """
        self.path = path
        self.format = format
        self.initial_last_modified = initial_last_modified

    @property
    def path(self) -> str | List[str]:
        """
        str | List[str]: The path or paths to the files to load.
        """
        return self._path

    @path.setter
    def path(self, path: str | List[str]):
        """
        Sets the path or paths to the files to load.

        Args:
            path (str | List[str]): The path or paths to the files to load.
        """
        self._path = path
        if isinstance(path, str):
            self._path_list = [path]
        elif isinstance(path, list):
            self._path_list = path
            if not all(isinstance(single_path, str) for single_path in self._path_list):
                raise InputConfigurationError(ErrorCode.ICE13, type(path))
        else:
            raise InputConfigurationError(ErrorCode.ICE13, type(path))

        for individual_path in self._path_list:
            if URI_INDICATOR in individual_path:
                parsed_path = urlparse(individual_path)
                if parsed_path.scheme != FILE_SCHEME:
                    raise InputConfigurationError(
                        ErrorCode.ICE14,
                        parsed_path.scheme,
                        FILE_SCHEME,
                        urlunparse(parsed_path),
                    )

        self._implicit_format_string = get_implicit_format_from_list(self._path_list)
        if hasattr(self, "_format") and self._format is None:
            # This check verifies that we are not in the __init__ function,
            # so we might have to check if the implicit format is valid or not.
            self._verify_valid_format(build_file_format(self._implicit_format_string))

    def to_dict(self) -> dict:
        """
        Converts the LocalFileInput object to a dictionary with all the relevant
            information.

        Returns:
            dict: A dictionary with the relevant information of the LocalFileInput
                object: path, format, and initial_last_modified.
        """
        return {
            self.IDENTIFIER: {
                self.FORMAT_KEY: self.format.to_dict(),
                self.LAST_MODIFIED_KEY: self.initial_last_modified,
                self.PATH_KEY: self._path_list,
            }
        }

    @property
    def format(self) -> FileFormat:
        """
        FileFormat: The format of the file or files. If not provided, it will be
            inferred  from the file extension in the path.
        """
        return self._format or build_file_format(self._implicit_format_string)

    @format.setter
    def format(self, format: str | dict | FileFormat):
        """
        Sets the format of the file.

        Args:
            format (str): The format of the file. If not
                provided, it will be inferred from the file extension of the file.
                Can be either a string with the format, a FileFormat object or a
                dictionary with the format as the 'type' key and any additional
                format-specific information. Currently supported formats are 'csv',
                'parquet', 'json' and 'log'.
        """
        if format is None:
            self._format = None
            # No format was provided, so we validate that self._implicit_format is valid
            self._verify_valid_format(build_file_format(self._implicit_format_string))
        else:
            # A format was provided
            format = build_file_format(format)
            self._verify_valid_format(format)
            self._format = format

    def _verify_valid_format(self, format: FileFormat):
        """
        Verifies that the provided format is valid for the LocalFileInput

        Args:
            format (FileFormat): The format to verify
        """
        valid_input_formats = tuple(element.value for element in self.SupportedFormats)
        if not (isinstance(format, valid_input_formats)):
            raise InputConfigurationError(
                ErrorCode.ICE4, type(format), valid_input_formats
            )

    @property
    def initial_last_modified(self) -> str:
        """
        str: The date and time after which the files were modified.
        """
        return (
            self._initial_last_modified.isoformat(timespec="microseconds")
            if self._initial_last_modified
            else None
        )

    @initial_last_modified.setter
    def initial_last_modified(self, initial_last_modified: str | datetime.datetime):
        """
        Sets the date and time after which the files were modified.

        Args:
            initial_last_modified (str | datetime.datetime): The date and time after
                which the files were modified. The date and time can be provided as a
                string in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601)
                or as a datetime object. If no timezone is
                provided, UTC will be assumed.
        """
        if initial_last_modified:
            if isinstance(initial_last_modified, datetime.datetime):
                self._initial_last_modified = initial_last_modified
            else:
                try:
                    self._initial_last_modified = datetime.datetime.fromisoformat(
                        initial_last_modified
                    )
                except ValueError:
                    raise InputConfigurationError(ErrorCode.ICE5, initial_last_modified)
                except TypeError:
                    raise InputConfigurationError(
                        ErrorCode.ICE6, type(initial_last_modified)
                    )
        else:
            self._initial_last_modified = None


class S3Input(Input):
    """
    Class for managing the configuration of S3-file-based data inputs.

    Attributes:
        format (FileFormat): The format of the file. If not provided, it will be
            inferred from the file extension of the data.
        uri (str | List[str]): The URI of the files with format: 's3://path/to/files'.
            It can be a single URI or a list of URIs.
        credentials (S3Credentials): The credentials required to access the S3 bucket.
        initial_last_modified (str | datetime.datetime): If provided, only the files
            modified after this date and time will be considered.

    Methods:
        to_dict(): Converts the S3Input object to a dictionary.
    """

    IDENTIFIER = InputIdentifiers.S3.value

    CREDENTIALS_KEY = "credentials"
    FORMAT_KEY = "format"
    LAST_MODIFIED_KEY = "initial_last_modified"
    REGION_KEY = "region"
    URI_KEY = "uri"

    class SupportedFormats(Enum):
        """
        Enum for the supported formats for the S3Input.
        """

        csv = CSVFormat
        json = NDJSONFormat
        log = LogFormat
        parquet = ParquetFormat

    # TODO: Consider making this a list calculated at runtime from existing regions.
    #   However, since they don't change that often, for now this should be good enough.
    class SupportedRegions(Enum):
        Ohio = "us-east-2"
        NorthVirginia = "us-east-1"
        NorthCalifornia = "us-west-1"
        Oregon = "us-west-2"
        CapeTown = "af-south-1"
        HongKong = "ap-east-1"
        Hyderabad = "ap-south-2"
        Jakarta = "ap-southeast-3"
        Malaysia = "ap-southeast-5"
        Melbourne = "ap-southeast-4"
        Mumbai = "ap-south-1"
        Osaka = "ap-northeast-3"
        Seoul = "ap-northeast-2"
        Singapore = "ap-southeast-1"
        Sydney = "ap-southeast-2"
        Tokyo = "ap-northeast-1"
        CanadaCentral = "ca-central-1"
        Calgary = "ca-west-1"
        Frankfurt = "eu-central-1"
        Ireland = "eu-west-1"
        London = "eu-west-2"
        Milan = "eu-south-1"
        Paris = "eu-west-3"
        Spain = "eu-south-2"
        Stockholm = "eu-north-1"
        Zurich = "eu-central-2"
        TelAviv = "il-central-1"
        Bahrain = "me-south-1"
        UAE = "me-central-1"
        SaoPaulo = "sa-east-1"
        GovCloudUSEast = "us-gov-east-1"
        GovCloudUSWest = "us-gov-west-1"

    def __init__(
        self,
        uri: str | List[str],
        credentials: dict | S3Credentials,
        format: str | dict | FileFormat = None,
        initial_last_modified: str | datetime.datetime = None,
        region: str = None,
    ):
        """
        Initializes the S3Input with the given URI and the credentials required to
            access the S3 bucket, and optionally a format and date and
            time after which the files were modified.

        Args:
            uri (str | List[str]): The URI of the files with format:
                's3://path/to/files'. It can be a single URI or a list of URIs.
            credentials (dict | S3Credentials): The credentials required to access the
                S3 bucket. Can be a dictionary or a S3Credentials object.
            format (str | dict | FileFormat, optional): The format of the file. If not
                provided, it will be inferred from the file extension of the data.
                Can be either a string with the format, a FileFormat object or a
                dictionary with the format as the 'type' key and any additional
                format-specific information. Currently supported formats are 'csv',
                'parquet', 'ndjson', 'jsonl' and 'log'.
            initial_last_modified (str | datetime.datetime, optional): If provided,
                only the files modified after this date and time will be considered.
                The date and time can be provided as a string in
                [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) or as
                a datetime object. If no timezone is provided, UTC will be assumed.
            region (str, optional): The region where the S3 bucket is located. If not
                provided, the default AWS region will be used.

        Raises:
            InputConfigurationError
            FormatConfigurationError
        """
        self.uri = uri
        self.format = format
        self.initial_last_modified = initial_last_modified
        self.credentials = credentials
        self.region = region

    @property
    def uri(self) -> str | List[str]:
        """
        str | List[str]: The URI of the files with format: 's3://path/to/files'.
        """
        return self._uri

    @uri.setter
    def uri(self, uri: str | List[str]):
        """
        Sets the URI of the files with format: 's3://path/to/files'.

        Args:
            uri (str | List[str]): The URI of the files with format:
                's3://path/to/files'. It can be a single URI or a list of URIs.
        """
        self._uri = uri
        if isinstance(uri, str):
            self._uri_list = [uri]
        elif isinstance(uri, list):
            self._uri_list = uri
            if not all(isinstance(single_uri, str) for single_uri in self._uri_list):
                raise InputConfigurationError(ErrorCode.ICE16, type(uri))
        else:
            raise InputConfigurationError(ErrorCode.ICE16, type(uri))

        self._parsed_uri_list = [urlparse(single_uri) for single_uri in self._uri_list]
        for parsed_uri in self._parsed_uri_list:
            if parsed_uri.scheme != S3_SCHEME:
                raise InputConfigurationError(
                    ErrorCode.ICE17,
                    parsed_uri.scheme,
                    S3_SCHEME,
                    urlunparse(parsed_uri),
                )

        self._implicit_format = get_implicit_format_from_list(self._uri_list)
        if hasattr(self, "_format") and self._format is None:
            self._verify_valid_format(build_file_format(self._implicit_format))

    def to_dict(self) -> dict:
        """
        Converts the S3Input object to a dictionary with all the relevant
            information.

        Returns:
            dict: A dictionary with the relevant information of the S3Input
                object: URI, format, credentials, last_modified time and region.
        """
        return {
            self.IDENTIFIER: {
                self.FORMAT_KEY: self.format.to_dict(),
                self.LAST_MODIFIED_KEY: self.initial_last_modified,
                self.URI_KEY: self._uri_list,
                self.CREDENTIALS_KEY: self.credentials.to_dict(),
                self.REGION_KEY: self.region,
            }
        }

    @property
    def region(self) -> str | None:
        """
        str: The region where the S3 bucket is located.
        """
        return self._region

    @region.setter
    def region(self, region: str | None):
        """
        Sets the region where the S3 bucket is located.

        Args:
            region (str): The region where the S3 bucket is located.
        """
        if region:
            if not isinstance(region, str):
                raise InputConfigurationError(ErrorCode.ICE26, type(region))
            supported_regions = [element.value for element in self.SupportedRegions]
            if region not in supported_regions:
                logger.warning(
                    "The 'region' parameter for the S3FileInput object has value "
                    f"'{region}', which is not recognized in our current list of AWS "
                    f"regions: {supported_regions}. This could indicate a typo in the "
                    "region provided, but it could also occur because you are "
                    "using a recently created AWS region or a private AWS region. "
                    "You can continue using this region if you are sure it is available"
                    " for your AWS account, but if it isn't it will cause an error "
                    "during runtime."
                )
            self._region = region
        else:
            self._region = None

    @property
    def format(self) -> FileFormat:
        """
        FileFormat: The format of the file. If not provided, it will be inferred from
            the file.
        """
        return self._format or build_file_format(self._implicit_format)

    @format.setter
    def format(self, format: str | dict | FileFormat):
        """
        Sets the format of the file.

        Args:
            format (str | dict | FileFormat): The format of the file. If not
                provided, it will be inferred from the file extension of the data.
                Can be either a string with the format, a FileFormat object or a
                dictionary with the format as the 'type' key and any additional
                format-specific information. Currently supported formats are 'csv',
                'parquet', 'ndjson', 'jsonl' and 'log'.
        """
        if format is None:
            self._format = None
            # No format was provided, so we validate that self._implicit_format is valid
            self._verify_valid_format(build_file_format(self._implicit_format))
        else:
            format = build_file_format(format)
            self._verify_valid_format(format)
            self._format = format

    def _verify_valid_format(self, format: FileFormat):
        """
        Verifies that the provided format is valid for the S3Input

        Args:
            format (FileFormat): The format to verify.
        """
        valid_input_formats = tuple(element.value for element in self.SupportedFormats)
        if not (isinstance(format, valid_input_formats)):
            raise InputConfigurationError(
                ErrorCode.ICE4, type(format), valid_input_formats
            )

    @property
    def initial_last_modified(self) -> str:
        """
        str: The date and time after which the files were modified.
        """
        return (
            self._initial_last_modified.isoformat(timespec="microseconds")
            if self._initial_last_modified
            else None
        )

    @initial_last_modified.setter
    def initial_last_modified(self, initial_last_modified: str | datetime.datetime):
        """
        Sets the date and time after which the files were modified.

        Args:
            initial_last_modified (str | datetime.datetime): The date and time after
                which the files were modified. The date and time can be provided as a
                string in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601)
                or as a datetime object. If no timezone is
                provided, UTC will be assumed.
        """
        if initial_last_modified:
            if isinstance(initial_last_modified, datetime.datetime):
                self._initial_last_modified = initial_last_modified
            else:
                try:
                    self._initial_last_modified = datetime.datetime.fromisoformat(
                        initial_last_modified
                    )
                except ValueError:
                    raise InputConfigurationError(ErrorCode.ICE5, initial_last_modified)
                except TypeError:
                    raise InputConfigurationError(
                        ErrorCode.ICE6, type(initial_last_modified)
                    )
        else:
            self._initial_last_modified = None

    @property
    def credentials(self) -> S3Credentials:
        """
        S3Credentials: The credentials required to access the S3 bucket.
        """
        return self._credentials

    @credentials.setter
    def credentials(self, credentials: dict | S3Credentials):
        """
        Sets the credentials required to access the S3 bucket.

        Args:
            credentials (dict | S3Credentials): The credentials required to access the
                S3 bucket. Can be a dictionary or a S3Credentials object.
        """
        credentials = build_credentials(credentials)
        if not (isinstance(credentials, S3Credentials)):
            raise InputConfigurationError(ErrorCode.ICE20, type(credentials))
        self._credentials = credentials


class MySQLInput(Input):
    """
    Class for managing the configuration of MySQL-based data inputs.

    Attributes:
        credentials (UserPasswordCredentials): The credentials required to access the
            MySQL database.
        initial_values (dict): The initial values for the parameters in the SQL queries.
        query (str | List[str]): The SQL query(s) to execute. If multiple queries are
            provided, they must be provided as a dictionary, with the parameter name in
            the registered function as the key and the SQL query as the value.
        uri (str): The URI of the database where the data is located.

    Methods:
        to_dict(): Converts the MySQLInput object to a dictionary.
    """

    IDENTIFIER = InputIdentifiers.MYSQL.value

    CREDENTIALS_KEY = "credentials"
    INITIAL_VALUES_KEY = "initial_values"
    QUERY_KEY = "query"
    URI_KEY = "uri"

    def __init__(
        self,
        uri: str,
        query: str | List[str],
        credentials: dict | UserPasswordCredentials | None = None,
        initial_values: dict | None = None,
    ):
        """
        Initializes the MySQLInput with the given URI and query, and optionally
            connection credentials and initial values for the parameters in the SQL
            queries.

        Args:
            uri (str): The URI of the database where the data is located
            query (str | List[str]): The SQL query(s) to execute. If multiple queries
                are provided, they must be provided as a list, and they will be
                mapped to the function inputs in the same order as they are defined.
            credentials (dict | UserPasswordCredentials, optional): The credentials
                required to access the MySQL database. Can be a dictionary or a
                UserPasswordCredentials object.
            initial_values (dict, optional): The initial values for the parameters in
                the SQL queries.

        Raises:
            InputConfigurationError
        """
        self.credentials = credentials
        self.uri = uri
        self.query = query
        self.initial_values = initial_values

    @property
    def uri(self) -> str:
        """
        str: The URI of the database where the data is located.
        """
        return self._uri

    @uri.setter
    def uri(self, uri: str):
        """
        Sets the URI of the database where the data is located.

        Args:
            uri (str): The URI of the database where the data is located.
        """
        self._uri = uri
        self._parsed_uri = urlparse(uri)
        if self._parsed_uri.scheme != MYSQL_SCHEME:
            raise InputConfigurationError(
                ErrorCode.ICE2, self._parsed_uri.scheme, MYSQL_SCHEME, self.uri
            )

        self.host, self.port = self._parsed_uri.netloc.split(":")
        self.database = self._parsed_uri.path[1:]

    @property
    def initial_values(self) -> dict:
        """
        dict: The initial values for the parameters in the SQL queries.
        """
        return self._initial_values

    @initial_values.setter
    def initial_values(self, initial_values: dict | None):
        """
        Sets the initial values for the parameters in the SQL queries.

        Args:
            initial_values (dict): The initial values for the parameters in the SQL
                queries.
        """
        if not initial_values:
            self._initial_values = {}
        elif not isinstance(initial_values, dict):
            raise InputConfigurationError(ErrorCode.ICE12, type(initial_values))
        else:
            self._initial_values = initial_values

    @property
    def query(self) -> str | List[str]:
        """
        str | List[str]: The SQL query(s) to execute.
        """
        return self._query

    @query.setter
    def query(self, query: str | List[str]):
        """
        Sets the SQL query(s) to execute

        Args:
            query (str | List[str]): The SQL query(s) to execute. If multiple queries
                are provided, they must be provided as a list, and they will be
                mapped to the function inputs in the same order as they are defined.
        """
        if isinstance(query, str):
            self._query = query
        elif isinstance(query, list):
            self._query = query
            if not all(isinstance(single_query, str) for single_query in self._query):
                raise InputConfigurationError(ErrorCode.ICE19, type(query))
        else:
            raise InputConfigurationError(ErrorCode.ICE19, type(query))

    @property
    def credentials(self) -> UserPasswordCredentials | None:
        """
        UserPasswordCredentials | None: The credentials required to access the
            MySQLDatabase. If no credentials were provided, it will return None.
        """
        return self._credentials

    @credentials.setter
    def credentials(self, credentials: dict | UserPasswordCredentials | None):
        """
        Sets the credentials to access the MySQLDatabase.

        Args:
            credentials (dict | UserPasswordCredentials | None): The credentials
                required to access the MySQLDatabase. Can be a UserPasswordCredentials
                object, a dictionary or None
        """
        if not credentials:
            self._credentials = None
        else:
            credentials = build_credentials(credentials)
            if not (isinstance(credentials, UserPasswordCredentials)):
                raise InputConfigurationError(ErrorCode.ICE22, type(credentials))
            self._credentials = credentials

    def to_dict(self) -> dict:
        """
        Converts the MySQLInput object to a dictionary with all the relevant
            information.

        Returns:
            dict: A dictionary with the relevant information of the MySQLInput
                object: URI, data, and configurations.
        """
        return {
            self.IDENTIFIER: {
                self.INITIAL_VALUES_KEY: self.initial_values,
                self.QUERY_KEY: self.query,
                self.URI_KEY: self.uri,
                self.CREDENTIALS_KEY: (
                    self.credentials.to_dict() if self.credentials else None
                ),
            }
        }


class TableInput(Input):
    """
    Class for managing the configuration of table-based data inputs.

    Attributes:
        uri (URI | List[URI]): The URI(s) of the table(s) to load.

    Methods:
        to_dict(): Converts the TableInput object to a dictionary.
    """

    IDENTIFIER = InputIdentifiers.TABLE.value

    URI_KEY = "uri"

    def __init__(self, uri: str | List[str] | URI | List[URI]):
        """
        Initializes the TableInput with the given URI. The URI must contain the table
            name. If multiple URIs are provided, they must be provided as a list.

        Args:
            uri (str | List[str] | URI | List[URI]): The URI(s) of the table(s) to load.
                If multiple URIs are provided, they must be provided as a list.
        """
        self.uri = uri

    @property
    def uri(self) -> URI | List[URI]:
        """
        URI | List[URI]: The URI(s) of the table(s) to load.
        """
        return self._uri

    @uri.setter
    def uri(self, uri: str | List[str] | URI | List[URI]):
        """
        Sets the URI(s) of the table(s) to load.

        Args:
            uri (str | List[str] | URI | List[URI]): The URI(s) of the table(s) to load.
                If multiple URIs are provided, they must be provided as a list
        """
        self._uri = uri
        if isinstance(uri, list):
            self._uri = [build_uri_object(single_uri) for single_uri in uri]
            self._uri_list = self._uri
        else:
            self._uri = build_uri_object(uri)
            self._uri_list = [self._uri]
        self._verify_valid_uri_list()

    def _verify_valid_uri_list(self):
        """
        Verifies that the URIs in the list are valid.
        """
        for single_uri in self._uri_list:
            if not single_uri.table:
                raise InputConfigurationError(ErrorCode.ICE25, single_uri)

    def to_dict(self) -> dict:
        """
        Converts the TableInput object to a dictionary with all the relevant
            information.

        Returns:
            dict: A dictionary with the relevant information of the Output
                object.
        """
        return {
            self.IDENTIFIER: {self.URI_KEY: [uri.to_string() for uri in self._uri_list]}
        }


class Output(ABC):
    """
    Abstract base class for managing data output configurations.
    """

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert the Output object to a dictionary with all
            the relevant information.

        Returns:
            dict: A dictionary with the relevant information of the Output
                object.
        """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Output):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Output.

        Returns:
            str: A string representation of the Output.
        """
        return f"{self.__class__.__name__}({self.to_dict()[self.IDENTIFIER]})"


class MySQLOutput(Output):
    """
    Class for managing the configuration of MySQL-based data outputs.

    Attributes:
        credentials (UserPasswordCredentials): The credentials required to access the
            MySQL database.
        destination_table (str | List[str]): The table(s) to create. If multiple tables
            are provided, they must be provided as a list.
        uri (str): The URI of the database where the data is going to be stored.

    Methods:
        to_dict(): Converts the MySQLOutput object to a dictionary
    """

    IDENTIFIER = OutputIdentifiers.MYSQL.value

    CREDENTIALS_KEY = "credentials"
    DESTINATION_TABLE_KEY = "destination_table"
    URI_KEY = "uri"

    def __init__(
        self,
        uri: str,
        destination_table: List[str] | str,
        credentials: dict | UserPasswordCredentials = None,
    ):
        """
        Initializes the MySQLOutput with the given URI and destination table,
        and optionally connection credentials.

        Args:
            uri (str): The URI of the database where the data is going to be stored.
            destination_table (List[str] | str): The tables to create. If multiple
                tables are provided, they must be provided as a list.
            credentials (dict | UserPasswordCredentials, optional): The credentials
                required to access the MySQL database. Can be a dictionary or a
                UserPasswordCredentials object.

        Raises:
            InputConfigurationError
        """
        self.credentials = credentials
        self.uri = uri
        self.destination_table = destination_table

    def to_dict(self) -> dict:
        """
        Converts the MySQLOutput object to a dictionary with all the relevant
            information.

        Returns:
            dict: A dictionary with the relevant information of the MySQLOutput
                object: URI, destination table, and credentials.
        """
        return {
            self.IDENTIFIER: {
                self.URI_KEY: self.uri,
                self.DESTINATION_TABLE_KEY: self.destination_table,
                self.CREDENTIALS_KEY: (
                    self.credentials.to_dict() if self.credentials else None
                ),
            }
        }

    @property
    def uri(self) -> str:
        """
        str: The URI of the database where the data is going to be stored.
        """
        return self._uri

    @uri.setter
    def uri(self, uri: str):
        """
        Sets the URI of the database where the data is going to be stored.

        Args:
            uri (str): The URI of the database where the data is going to be stored.
        """
        self._uri = uri
        self._parsed_uri = urlparse(uri)
        if self._parsed_uri.scheme != MYSQL_SCHEME:
            raise OutputConfigurationError(
                ErrorCode.OCE2, self._parsed_uri.scheme, MYSQL_SCHEME, self.uri
            )
        self.host, self.port = self._parsed_uri.netloc.split(":")
        self.database = self._parsed_uri.path[1:]

    @property
    def destination_table(self) -> str | List[str]:
        """
        str | List[str]: The table(s) to create. If multiple tables are provided,
            they must be provided as a list.
        """
        return self._destination_table

    @destination_table.setter
    def destination_table(self, destination_table: List[str] | str):
        """
        Sets the table(s) to create.

        Args:
            destination_table (List[str] | str): The table(s) to create. If multiple
                tables are provided, they must be provided as a list.
        """
        if isinstance(destination_table, (list, str)):
            self._destination_table = destination_table
        else:
            raise OutputConfigurationError(ErrorCode.OCE8, type(destination_table))

    @property
    def credentials(self) -> UserPasswordCredentials:
        """
        UserPasswordCredentials: The credentials required to access the MySQLDatabase.
        """
        return self._credentials

    @credentials.setter
    def credentials(self, credentials: dict | UserPasswordCredentials | None):
        """
        Sets the credentials to access the MySQLDatabase.

        Args:
            credentials (dict | UserPasswordCredentials | None): The credentials
                required to access the MySQLDatabase. Can be a
                UserPasswordCredentials object, a dictionary or None if no
                credentials are needed.
        """
        if not credentials:
            self._credentials = None
        else:
            credentials = build_credentials(credentials)
            if not (isinstance(credentials, UserPasswordCredentials)):
                raise OutputConfigurationError(ErrorCode.OCE9, type(credentials))
            self._credentials = credentials


class TableOutput(Output):
    """
    Class for managing the configuration of table-based data outputs.

    Attributes:
        table (str | List[str]): The table(s) to create. If multiple tables are
            provided, they must be provided as a list.

    Methods:
        to_dict(): Converts the TableOutput object to a dictionary
    """

    IDENTIFIER = OutputIdentifiers.TABLE.value

    TABLE_KEY = "table"

    def __init__(self, table: str | List[str]):
        """
        Initializes the TableOutput with the given table(s) to create.

        Args:
            table (str | List[str]): The table(s) to create. If multiple tables are
                provided, they must be provided as a list.
        """
        self.table = table

    @property
    def table(self) -> str | List[str]:
        """
        str | List[str]: The table(s) to create. If multiple tables are provided,
            they must be provided as a list.
        """
        return self._table

    @table.setter
    def table(self, table: str | List[str]):
        """
        Sets the table(s) to create.

        Args:
            table (str | List[str]): The table(s) to create. If multiple tables are
                provided, they must be provided as a list.
        """
        self._table = table
        self._table_list = table if isinstance(table, list) else [table]
        for single_table in self._table_list:
            if not isinstance(single_table, str):
                raise OutputConfigurationError(
                    ErrorCode.OCE10, single_table, type(single_table)
                )

    def to_dict(self) -> dict:
        """
        Converts the TableOutput object to a dictionary with all the relevant
        information.
        """
        return {self.IDENTIFIER: {self.TABLE_KEY: self._table_list}}


def build_input(input: dict | Input | None) -> Input | None:
    """
    Builds an Input object.

    Args:
        input (dict | Input | None): A dictionary with the input information or an
            Input object.

    Returns:
        Input: A Input object built from the input.
            It can be a LocalFileInput, S3FileInput, MySQLInput, or TableInput
            object, or None if nothing was provided

    Raises:
        InputConfigurationError
    """
    if not input:
        return None
    elif isinstance(input, Input):
        return input
    elif isinstance(input, dict):
        return build_input_from_dict(input)
    else:
        raise InputConfigurationError(ErrorCode.ICE11, type(input))


def build_input_from_dict(input: dict) -> Input:
    valid_identifiers = [element.value for element in InputIdentifiers]
    # The input dictionary must have exactly one key, which must be one of the
    # valid identifiers
    if len(input) != 1 or next(iter(input)) not in valid_identifiers:
        raise InputConfigurationError(
            ErrorCode.ICE7, valid_identifiers, list(input.keys())
        )
    # Since we have only one key, we select the identifier and the configuration
    identifier, configuration = next(iter(input.items()))
    # The configuration must be a dictionary
    if not isinstance(configuration, dict):
        raise InputConfigurationError(ErrorCode.ICE8, identifier, type(configuration))
    if identifier == LocalFileInput.IDENTIFIER:
        return LocalFileInput(**configuration)
    elif identifier == S3Input.IDENTIFIER:
        return S3Input(**configuration)
    elif identifier == MySQLInput.IDENTIFIER:
        return MySQLInput(**configuration)
    elif identifier == TableInput.IDENTIFIER:
        return TableInput(**configuration)
    elif identifier == AzureInput.IDENTIFIER:
        return AzureInput(**configuration)


# TODO: Explore unifying the build_input and build_output functions into a single
#   function, make them use a common codebase or even create a BuildIO class to
#   encapsulate both of them. Waiting to see the development of both functions to
#   decide.
#   https://tabsdata.atlassian.net/browse/TAB-47
def build_output(output: dict | Output | None) -> Output | None:
    """
    Builds an Output object.

    Args:
        output (dict | Output | None): A dictionary with the output information,
            or an Output object.

    Returns:
        Output: A Output object built from the output.
            That can be a MySQLOutput or Table Output object, or None if nothing was
            provided.

    Raises:
        OutputConfigurationError
    """
    valid_identifiers = [element.value for element in OutputIdentifiers]
    if not output:
        return None
    elif isinstance(output, Output):
        return output
    elif isinstance(output, dict):
        # The output dictionary must have exactly one key, which must be one of the
        # valid identifiers
        if len(output) != 1 or next(iter(output)) not in valid_identifiers:
            raise OutputConfigurationError(
                ErrorCode.OCE3, valid_identifiers, list(output.keys())
            )
        # Since we have only one key, we select the identifier and the configuration
        identifier, configuration = next(iter(output.items()))
        # The configuration must be a dictionary
        if not isinstance(configuration, dict):
            raise OutputConfigurationError(
                ErrorCode.OCE4, identifier, type(configuration)
            )
        if identifier == MySQLOutput.IDENTIFIER:
            return MySQLOutput(**configuration)
        elif identifier == TableOutput.IDENTIFIER:
            return TableOutput(**configuration)
    else:
        raise OutputConfigurationError(ErrorCode.OCE7, type(output))


class DatasetFunction:
    """
    Class to decorate a function with metadata and methods for use in a TabsData
        environment.

    Attributes:

    """

    def __init__(
        self,
        func: Callable,
        dataset_name: str,
        input: dict | Input | InputPlugin = None,
        output: dict | Output | OutputPlugin = None,
        trigger_by: str | URI | None = None,
    ):
        """
        Initializes the TabsDataFunction with the given function, input, output and
        trigger.

        Args:
            func (Callable): The function to decorate.
            dataset_name (str): The name of the dataset that the function will
                be registered to.
            input (dict | Input | InputPlugin, optional): The data to be used when
                running the function. Can be a dictionary or an instance of Input or
                InputPlugin.
            output (dict | Output | OutputPlugin, optional): The location where the
                function results will be saved when run.
            trigger_by (str, optional): The trigger that will cause the function to
            execute. It must be another dataset in the system.

        Raises:
            FunctionConfigurationError
            InputConfigurationError
            OutputConfigurationError
            FormatConfigurationError
        """
        self.original_function = func
        self.output = output
        self.input = input
        self._func_original_folder, self._func_original_file = os.path.split(
            inspect.getfile(func)
        )
        self.trigger_by = trigger_by
        self.dataset_name = dataset_name

    def __repr__(self) -> str:
        """
        Returns a string representation of the TabsDataFunction.

        Returns:
            str: A string representation of the TabsDataFunction.
        """
        return (
            f"{self.__class__.__name__}({self._func.__name__})(input='{self.input}',"
            f" output='{self.output}', original_file='{self.original_file}',"
            f" original_folder='{self.original_folder}', trigger='{self.trigger_by}')"
        )

    def __call__(self, *args, **kwargs):
        """
        Calls the original function with the given arguments and keyword arguments.

        Args:
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Any: The return value of the original function
        """
        return self._func(*args, **kwargs)

    @property
    def input(self) -> Input | InputPlugin | None:
        """
        Input | InputPlugin | None: The data to be used when running the function.
        """
        return self._input

    @input.setter
    def input(self, input: dict | Input | InputPlugin | None):
        """
        Sets the input data for the function.

        Args:
            input (dict | Input | None): The data to be used when running the
                function. Can be a dictionary, an instance of Input, an instance of
                InputPlugin or None.
        """
        if isinstance(input, InputPlugin):
            self._input = input
        else:
            self._input = build_input(input)
        self._verify_valid_input_output()

    @property
    def original_folder(self) -> str:
        """
        str: The folder where the original function is defined, as a local path in the
            user's computer.
        """
        return self._func_original_folder

    @property
    def original_file(self):
        """
        str: The file where the original function is defined in the user's computer
        """
        return self._func_original_file

    @property
    def original_function(self) -> Callable:
        """
        Callable: The original function that was decorated, without any behaviour
            modifications.
        """
        return self._func

    @original_function.setter
    def original_function(self, func: Callable):
        """
        Sets the original function for the TabsDataFunction.

        Args:
            func (Callable): The original function that was decorated, without any
                behaviour modifications.
        """
        if not callable(func):
            raise FunctionConfigurationError(ErrorCode.FCE1, type(func))
        self._func = func

    @property
    def output(self) -> Output | OutputPlugin | None:
        """
        dict: The location where the function results will be saved when run.
        """
        return self._output

    @output.setter
    def output(self, output: dict | Output | OutputPlugin | None):
        """
        Sets the output location for the function.

        Args:
            output (dict | Output | OutputPlugin | None): The location where the
                function results will be saved when run.
        """
        if isinstance(output, OutputPlugin):
            self._output = output
        else:
            self._output = build_output(output)
        self._verify_valid_input_output()

    @property
    def dataset_name(self) -> str:
        """
        str: The name of the dataset that the function will be registered to.
        """
        return self._dataset_name

    @dataset_name.setter
    def dataset_name(self, dataset_name: str):
        """
        Sets the name of the dataset that the function will be registered to.

        Args:
            dataset_name (str): The name of the dataset that the function will be
                registered to.
        """
        if isinstance(dataset_name, str):
            self._dataset_name = dataset_name
        else:
            raise FunctionConfigurationError(ErrorCode.FCE6, type(dataset_name))

    @property
    def trigger_by(self) -> URI | None:
        """
        URI | None: The trigger that will cause the function to execute. It must be
            another dataset in the system.
        """
        return self._trigger_by

    @trigger_by.setter
    def trigger_by(self, trigger_by: str | URI | None):
        """
        Sets the trigger that will cause the function to execute

        Args:
            trigger_by (str | URI | None): The trigger that will cause the function to
                execute. It must be another dataset in the system.
        """
        if not trigger_by:
            self._trigger_by = None
        elif isinstance(trigger_by, str):
            self._trigger_by = build_uri_object(trigger_by)
        elif isinstance(trigger_by, URI):
            self._trigger_by = trigger_by
        else:
            raise FunctionConfigurationError(ErrorCode.FCE2, type(trigger_by))

        if self._trigger_by and not self._trigger_by.dataset:
            raise FunctionConfigurationError(ErrorCode.FCE3, self._trigger_by)
        elif self._trigger_by and self._trigger_by.table:
            raise FunctionConfigurationError(ErrorCode.FCE4, self._trigger_by)

    def _verify_valid_input_output(self):
        """
        Verifies that the input and output are valid for the function.

        Raises:
            FunctionConfigurationError
        """
        if hasattr(self, "_input") and hasattr(self, "_output"):
            is_not_table_input = self.input and not isinstance(self.input, TableInput)
            is_not_table_output = self.output and not isinstance(
                self.output, TableOutput
            )
            if is_not_table_input and is_not_table_output:
                raise FunctionConfigurationError(
                    ErrorCode.FCE5, type(self.input), type(self.output)
                )
