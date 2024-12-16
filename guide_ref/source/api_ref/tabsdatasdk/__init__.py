#
# Copyright 2024 Tabs Data Inc.
#

import logging

from tabsdatasdk.api.tabsdata_server import (
    Dataset,
    Datastore,
    ExecutionPlan,
    TabsdataServer,
    User,
)
from tabsdatasdk.credentials import (
    AzureAccountKeyCredentials,
    S3AccessKeyCredentials,
    UserPasswordCredentials,
)
from tabsdatasdk.datasetfunction import (
    AzureInput,
    LocalFileInput,
    MySQLInput,
    MySQLOutput,
    S3Input,
    TableInput,
    TableOutput,
)
from tabsdatasdk.decorators import dataset
from tabsdatasdk.format import CSVFormat, LogFormat, NDJSONFormat, ParquetFormat
from tabsdatasdk.plugin import InputPlugin, OutputPlugin
from tabsdatasdk.secret import DirectSecret, EnvironmentSecret, HashiCorpSecret
from tabsdatasdk.uri import URI

logging.basicConfig(
    level=logging.getLevelName(logging.WARNING),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

__all__ = [
    # from tabsdatafunction.py Inputs
    "AzureInput",
    "LocalFileInput",
    "MySQLInput",
    "S3Input",
    "TableInput",
    # from tabsdatafunction.py Outputs
    "MySQLOutput",
    "TableOutput",
    # from plugin.py
    "InputPlugin",
    "OutputPlugin",
    # from decorators.py
    "dataset",
    # from format.py
    "CSVFormat",
    "LogFormat",
    "NDJSONFormat",
    "ParquetFormat",
    # from credentials.py
    "AzureAccountKeyCredentials",
    "S3AccessKeyCredentials",
    "UserPasswordCredentials",
    # from secret.py
    "DirectSecret",
    "EnvironmentSecret",
    "HashiCorpSecret",
    # from uri.py
    "URI",
    # from tabsdata_server.py
    "Dataset",
    "Datastore",
    "ExecutionPlan",
    "TabsdataServer",
    "User",
]
