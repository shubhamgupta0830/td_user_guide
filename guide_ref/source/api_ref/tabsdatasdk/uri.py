#
# Copyright 2024 Tabs Data Inc.
#

import re
from typing import List

from tabsdatasdk.exceptions import ErrorCode, URIConfigurationError

TABSDATA_SCHEME = "td"
URI_INDICATOR = "://"


class Version:
    """
    Version class to represent a Tabs Data version. The version is represented as a
        string. The version can be HEAD, HEAD^, HEAD^^, HEAD~1, HEAD~2, etc. or a
        26-character hexadecimal string (the hash of a specific commit).

    Attributes:
        version (str): The version of the URI.

    Methods:
        to_string() -> str: Return the version as a string.
    """

    VERSION_PATTERN = re.compile(r"^(HEAD\^*|HEAD~[0-9]+|[A-Z0-9]{26})$")

    def __init__(self, version: str):
        """
        Initialize the Version object.

        Args:
            version (str): The version of the URI.
        """
        self.version = version

    @property
    def version(self) -> str:
        """
        str: The version of the URI.
        """
        return self._version

    @version.setter
    def version(self, version: str):
        """
        Set the version of the URI.

        Args:
            version (str): The version of the URI.
        """
        if isinstance(version, str):
            if self.VERSION_PATTERN.match(version):
                self._version = version
            else:
                raise URIConfigurationError(
                    ErrorCode.UCE9, self.VERSION_PATTERN, version
                )
        else:
            raise URIConfigurationError(ErrorCode.UCE1, type(version))

    def to_string(self) -> str:
        """
        Return the version as a string.
        """
        return self.version

    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return False
        return self.to_string() == other.to_string()

    def __str__(self) -> str:
        return self.to_string()


class VersionList:
    """
    VersionList class to represent a list of Tabs Data versions. The version list is
        represented as a list of Version objects.

    Attributes:
        version_list (List[Version]): The list of versions of the URI.

    Methods:
        to_string() -> str: Return the version list as a string.
    """

    def __init__(self, version_list: List[Version] | List[str]):
        """
        Initialize the VersionList object.

        Args:
            version_list (List[Version] | List[str]): The list of versions of the URI.
        """
        self.version_list = version_list

    @property
    def version_list(self) -> List[Version]:
        """
        List[Version]: The list of versions of the URI.
        """
        return self._version_list

    @version_list.setter
    def version_list(self, version_list: List[str] | List[Version]):
        """
        Set the list of versions of the URI.

        Args:
            version_list (List[str] | List[Version]): The list of versions of the URI.
        """
        if isinstance(version_list, list):
            if len(version_list) > 1:
                self._version_list = [
                    build_version_object(version) for version in version_list
                ]
            else:
                raise URIConfigurationError(
                    ErrorCode.UCE8, version_list, len(version_list)
                )
        else:
            raise URIConfigurationError(ErrorCode.UCE6, list, type(version_list))

        for version in self._version_list:
            if not isinstance(version, Version):
                raise URIConfigurationError(
                    ErrorCode.UCE7, Version, version, type(version)
                )

    def to_string(self) -> str:
        """
        Return the version list as a string.

        Returns:
            str: The version list as a string.
        """
        return ",".join([version.to_string() for version in self.version_list])

    def __eq__(self, other) -> bool:
        if not isinstance(other, VersionList):
            return False
        return self.to_string() == other.to_string()

    def __str__(self) -> str:
        return self.to_string()


class VersionRange:
    """
    VersionRange class to represent a range of Tabs Data versions. The version range is
        represented as two Version objects, indicating the beginning and ending of
        the range.

    Attributes:
        initial_version (Version): The initial version of the range.
        final_version (Version): The final version of the range.

    Methods:
        to_string() -> str: Return the version range as a string.
    """

    def __init__(self, initial_version: str | Version, final_version: str | Version):
        """
        Initialize the VersionRange object.

        Args:
            initial_version (str | Version): The initial version of the range.
            final_version (str | Version): The final version of the range.
        """
        self.initial_version = initial_version
        self.final_version = final_version

    @property
    def initial_version(self) -> Version:
        """
        Version: The initial version of the range.
        """
        return self._initial_version

    @initial_version.setter
    def initial_version(self, initial_version: str | Version):
        """
        Set the initial version of the range.

        Args:
            initial_version (str | Version): The initial version of the range.
        """
        built_initial_version = build_version_object(initial_version)
        if isinstance(built_initial_version, Version):
            self._initial_version = built_initial_version
        else:
            raise URIConfigurationError(
                ErrorCode.UCE2,
                Version,
                built_initial_version,
                type(built_initial_version),
            )

    @property
    def final_version(self) -> Version:
        """
        Version: The final version of the range.
        """
        return self._final_version

    @final_version.setter
    def final_version(self, final_version: str | Version):
        """
        Set the final version of the range.

        Args:
            final_version (str | Version): The final version of the range.
        """
        built_final_version = build_version_object(final_version)
        if isinstance(built_final_version, Version):
            self._final_version = built_final_version
        else:
            raise URIConfigurationError(
                ErrorCode.UCE3, Version, built_final_version, type(built_final_version)
            )

    def to_string(self) -> str:
        """
        Return the version range as a string.

        Returns:
            str: The version range as a string.
        """
        return self.initial_version.to_string() + ".." + self.final_version.to_string()

    def __eq__(self, other) -> bool:
        if not isinstance(other, VersionRange):
            return False
        return self.to_string() == other.to_string()

    def __str__(self) -> str:
        return self.to_string()


def build_version_object(version: str | Version | VersionList | VersionRange):
    if isinstance(version, (Version, VersionRange, VersionList)):
        return version
    elif isinstance(version, str):
        if ".." in version:
            split_range = version.split("..")
            if len(split_range) == 2:
                return VersionRange(split_range[0], split_range[1])
            else:
                raise URIConfigurationError(ErrorCode.UCE5, version)
        elif "," in version:
            split_list = version.split(",")
            return VersionList(split_list)
        else:
            return Version(version)
    else:
        raise URIConfigurationError(
            ErrorCode.UCE4, [str, Version, VersionList, VersionRange], type(version)
        )


class URI:
    """
    URI class to represent a Tabs Data URI. The URI is composed of a datastore, a
        dataset, a table and a version. The URI is represented as
        td://datastore/dataset/table@version or td://dataset/table@version. The
        datastore, dataset and table are optional, but at least one of them must be
        present. The version is optional. The datastore, dataset and table must be
        strings. The version can be a string, a Version object, a VersionList object
        or a VersionRange object.

    Attributes:
        datastore (str): The datastore of the URI.
        dataset (str): The dataset of the URI.
        table (str): The table of the URI.
        version (Version | VersionList | VersionRange | None): The version of the URI.

    Methods:
        to_string() -> str: Return the URI as a string.
    """

    def __init__(
        self,
        datastore: str | None = None,
        dataset: str | None = None,
        table: str | None = None,
        version: str | Version | VersionList | VersionRange | None = None,
    ):
        """
        Initialize the URI object.

        Args:
            datastore (str | None): The datastore of the URI.
            dataset (str | None): The dataset of the URI.
            table (str | None): The table of the URI.
            version (str | Version | VersionList | VersionRange | None): The version of
                the URI. If it is a string, it can be a single version, a list of
                versions separated by commas or a range of versions separated by two
                dots. If it is a Version, VersionList or VersionRange object, it will be
                used as is.
        """
        self._fully_built = False
        self.datastore = datastore
        self.dataset = dataset
        self.table = table
        self.version = version
        self._verify_valid_uri()
        self._fully_built = True

    @property
    def datastore(self) -> str:
        """
        str: The datastore of the URI.
        """
        return self._datastore

    @datastore.setter
    def datastore(self, datastore: str | None):
        """
        Set the datastore of the URI.

        Args:
            datastore (str | None): The datastore of the URI.
        """
        if datastore is None:
            self._datastore = ""
        elif isinstance(datastore, str):
            self._datastore = datastore
        else:
            raise URIConfigurationError(ErrorCode.UCE10, type(datastore))
        if self._fully_built:
            self._verify_valid_uri()

    @property
    def dataset(self) -> str:
        """
        str: The dataset of the URI.
        """
        return self._dataset

    @dataset.setter
    def dataset(self, dataset: str | None):
        """
        Set the dataset of the URI.

        Args:
            dataset (str | None): The dataset of the URI.
        """
        if dataset is None:
            self._dataset = ""
        elif isinstance(dataset, str):
            self._dataset = dataset
        else:
            raise URIConfigurationError(ErrorCode.UCE11, type(dataset))
        if self._fully_built:
            self._verify_valid_uri()

    @property
    def table(self) -> str:
        """
        str: The table of the URI.
        """
        return self._table

    @table.setter
    def table(self, table: str | None):
        """
        Set the table of the URI.

        Args:
            table (str | None): The table of the URI.
        """
        if table is None:
            self._table = ""
        elif isinstance(table, str):
            self._table = table
        else:
            raise URIConfigurationError(ErrorCode.UCE12, type(table))
        if self._fully_built:
            self._verify_valid_uri()

    @property
    def version(self) -> Version | VersionList | VersionRange | None:
        """
        Version | VersionList | VersionRange | None: The version(s) of the URI.
        """
        return self._version

    @version.setter
    def version(self, version: str | Version | VersionList | VersionRange | None):
        """
        Set the version of the URI.

        Args:
            version (str | Version | VersionList | VersionRange | None): The
                version(s) of the URI. If it is a string, it can be a single version,
                a list of versions separated by commas or a range of versions separated
                by two dots. If it is a Version, VersionList or VersionRange object, it
                will be used as is.
        """
        if version is None:
            self._version = None
        else:
            self._version = build_version_object(version)
        if self._fully_built:
            self._verify_valid_uri()

    def to_string(self) -> str:
        """
        Return the URI as a string.

        Returns:
            str: The URI as a string.
        """
        if self.datastore:
            uri = f"{TABSDATA_SCHEME}{URI_INDICATOR}/{self.datastore}"
            if self.dataset:
                uri += f"/{self.dataset}"
        else:
            uri = f"{TABSDATA_SCHEME}{URI_INDICATOR}{self.dataset}"
        if self.table:
            uri += f"/{self.table}"
        if self.version:
            uri += "@" + self.version.to_string()
        return uri

    def _verify_valid_uri(self):
        """
        Verify that the URI is valid. It must have at least a datastore or a dataset,
            and if it has a table, it must have a dataset.
        """
        if not self.dataset and not self.datastore:
            raise URIConfigurationError(ErrorCode.UCE15)
        if not self.dataset and self.table:
            raise URIConfigurationError(ErrorCode.UCE16)

    def __eq__(self, other) -> bool:
        if not isinstance(other, URI):
            return False
        return self.to_string() == other.to_string()

    def __str__(self) -> str:
        return self.to_string()


def build_uri_object(uri: str | URI) -> URI:
    original_uri = uri
    if isinstance(uri, URI):
        return uri
    elif isinstance(uri, str):
        uri_prefix = TABSDATA_SCHEME + URI_INDICATOR
        if uri.startswith(uri_prefix + "/"):
            # We are working with a URI string of the form
            # td://datastore</dataset></table><@versions>
            # We remove the third slash and then match it with a regex
            uri = uri[len(uri_prefix) + 1 :]
            pattern = re.compile(
                r"^(?P<datastore>[^/@]+)(?:/(?P<dataset>[^/@]+)(?:/(?P<table>[^/@]+)("
                r"?:@(?P<version>[^/@]+))?)?|@(?P<version2>[^/@]+)|/(?P<dataset2>["
                r"^/@]+)@(?P<version3>[^/@]+))?$"
            )
            match = pattern.match(uri)
            if match:
                return URI(
                    match.group("datastore"),
                    match.group("dataset") or match.group("dataset2"),
                    match.group("table"),
                    match.group("version")
                    or match.group("version2")
                    or match.group("version3"),
                )
            else:
                raise URIConfigurationError(ErrorCode.UCE13, original_uri)
        elif uri.startswith(uri_prefix):
            # We are working with a URI string of the form
            # td://dataset</table><@versions>
            uri = uri[len(uri_prefix) :]
            pattern = re.compile(
                "^(?P<dataset>[^/@]+)(?:/(?P<table>[^/@]+)(?:@("
                "?P<version>[^/@]+))?|@(?P<version2>[^/@]+))?$"
            )
            match = pattern.match(uri)
            if match:
                return URI(
                    None,
                    match.group("dataset"),
                    match.group("table"),
                    match.group("version") or match.group("version2"),
                )
            else:
                raise URIConfigurationError(ErrorCode.UCE13, original_uri)
        else:
            raise URIConfigurationError(ErrorCode.UCE13, original_uri)
    else:
        raise URIConfigurationError(ErrorCode.UCE14, type(original_uri))
