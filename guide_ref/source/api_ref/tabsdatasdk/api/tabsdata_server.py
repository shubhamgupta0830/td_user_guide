#
# Copyright 2024 Tabs Data Inc.
#

import datetime
import hashlib
import importlib.util
import inspect
import os
import sys
import tempfile
from typing import List

import requests

from tabsdatasdk.api.api_server import obtain_connection
from tabsdatasdk.datasetfunction import DatasetFunction, TableInput, TableOutput
from tabsdatasdk.uri import URI
from tabsdatasdk.utils.bundle_utils import create_bundle_archive


class ExecutionPlan:
    """
    This class represents an execution plan in the TabsdataServer.

    Args:
        datastore (str): The datastore where the execution plan is running.
        dataset (str): The dataset where the execution plan is running.
        triggered_by (str): The user that triggered the execution plan.
        triggered_on (int): The timestamp when the execution plan was triggered.
        ended_on (int): The timestamp when the execution plan ended.
        started_on (int): The timestamp when the execution plan started.
        status (str): The status of the execution plan.
        **kwargs: Additional keyword arguments.

    Attributes:
        STATUS_MAPPING (dict): A dictionary mapping the status of the execution plan to
            a human-readable string.
        triggered_on_str (str): The timestamp when the execution plan was triggered as a
            string.
        ended_on_str (str): The timestamp when the execution plan ended as a string.
        started_on_str (str): The timestamp when the execution plan started as a string.

    Methods:
        status_to_mapping(status: str) -> str: Convert the status of the execution plan
            to a human-readable string.
    """

    STATUS_MAPPING = {
        "C": "Cancelled",
        "D": "Done",
        "E": "Error",
        "F": "Failed",
        "R": "Running",
        "S": "Scheduled",
    }

    def status_to_mapping(self, status: str) -> str:
        """
        Function to convert an execution_plan status to a mapping. While currently it
        only accesses the dictionary and returns the corresponding value, it could get
        more difficult in the future.
        """
        return self.STATUS_MAPPING[status]

    def __init__(
        self,
        datastore: str,
        dataset: str,
        triggered_by: str,
        triggered_on: int,
        ended_on: int,
        started_on: int,
        status: str,
        **kwargs,
    ):
        """
        Initialize the ExecutionPlan object.

        Args:
            datastore (str): The datastore where the execution plan is running.
            dataset (str): The dataset where the execution plan is running.
            triggered_by (str): The user that triggered the execution plan.
            triggered_on (int): The timestamp when the execution plan was triggered.
            ended_on (int): The timestamp when the execution plan ended.
            started_on (int): The timestamp when the execution plan started.
            status (str): The status of the execution plan.
            **kwargs: Additional keyword arguments.
        """
        self.datastore = datastore
        self.dataset = dataset
        self.triggered_by = triggered_by
        self.triggered_on = triggered_on
        self.triggered_on_str = convert_timestamp_to_string(self.triggered_on)
        self.raw_status = status
        self.ended_on = ended_on
        self.ended_on_str = convert_timestamp_to_string(self.ended_on)
        self.started_on = started_on
        self.started_on_str = convert_timestamp_to_string(self.started_on)
        self.status = self.status_to_mapping(status)
        self.kwargs = kwargs

    def __repr__(self) -> str:
        repr = (
            f"{self.__class__.__name__}(datastore={self.datastore!r},"
            f"dataset={self.dataset!r},"
            f"triggered_by={self.triggered_by!r},"
            f"triggered_on={self.triggered_on_str!r},"
            f"status={self.status!r}"
        )
        return repr

    def __str__(self) -> str:
        string = (
            f"Datastore: {self.datastore!s}, "
            f"dataset : {self.dataset!s}, "
            f"triggered by: '{self.triggered_by!s}', "
            f"triggered on: {self.triggered_on_str!s}, "
            f"status: {self.status!s}"
        )
        return string


class Function:
    """
    This class represents a function in the TabsdataServer.

    Args:
        trigger_with_names (str | None): If not None, the URI of the trigger of the
            function.
        tables (List[str]): The tables generated the function.
        dependencies_with_names (List[str]): The dependencies of the function.
        name (str): The name of the function.
        description (str): The description of the function.
        created_on (int): The timestamp when the function was created.
        created_by (str): The user that created the function.
        **kwargs: Additional keyword arguments.

    Attributes:
        created_on_string (str): The timestamp when the function was created as a
            string.
    """

    def __init__(
        self,
        trigger_with_names: str | None,
        tables: List[str],
        dependencies_with_names: List[str],
        name: str = None,
        description: str = None,
        created_on: int = None,
        created_by: str = None,
        **kwargs,
    ):
        """
        Initialize the Function object.

        Args:
            trigger_with_names (str | None): If not None, the URI of the trigger of the
                function.
            tables (List[str]): The tables generated the function.
            dependencies_with_names (List[str]): The dependencies of the function.
            name (str): The name of the function.
            description (str): The description of the function.
            created_on (int): The timestamp when the function was created.
            created_by (str): The user that created the function.
            **kwargs: Additional keyword arguments.
        """
        self.trigger_with_names = trigger_with_names
        self.tables = tables
        self.dependencies_with_names = dependencies_with_names
        self.name = name
        self.description = description
        self.created_on = created_on
        self.created_on_string = convert_timestamp_to_string(created_on)
        self.created_by = created_by
        self.kwargs = kwargs

    def __repr__(self) -> str:
        representation = f"{self.__class__.__name__}("
        if self.name:
            representation += f"name={self.name!r},"
        if self.description:
            representation += f"description={self.description!r},"
        if self.created_on:
            representation += f"created_on={self.created_on_string!r},"
        if self.created_by:
            representation += f"created_by={self.created_by!r},"
        representation += (
            f"dependencies_with_names={self.dependencies_with_names!r},"
            f"trigger_with_names={self.trigger_with_names!r},"
            f"tables={self.tables!r})"
        )
        return representation

    def __str__(self) -> str:
        string_representation = ""
        if self.name:
            string_representation += f"Name: {self.name!s}, "
        if self.description:
            string_representation += f"description: '{self.description!s}', "
        if self.created_on:
            string_representation += f"created on: {self.created_on_string!s}, "
        if self.created_by:
            string_representation += f"created by: {self.created_by!s}, "
        string_representation += (
            f"dependency URIs: {self.dependencies_with_names!s}, "
            f"trigger URI: {self.trigger_with_names!s}, "
            f"tables: {self.tables!s}"
        )
        return string_representation


class Dataset:
    """
    This class represents a dataset in the TabsdataServer.

    Args:
        name (str): The name of the dataset.
        datastore (str): The datastore where the dataset is stored.
        created_on (int): The timestamp when the dataset was created.
        created_by (str): The user that created the dataset.
        description (str): The description of the dataset.
        function (Function): The function of the dataset.
        **kwargs: Additional keyword arguments.

    Attributes:
        created_on_string (str): The timestamp when the dataset was created as a string.
    """

    def __init__(
        self,
        name: str,
        datastore: str,
        created_on: int,
        created_by: str,
        description: str,
        function: Function = None,
        **kwargs,
    ):
        """
        Initialize the Dataset object.

        Args:
            name (str): The name of the dataset.
            datastore (str): The datastore where the dataset is stored.
            created_on (int): The timestamp when the dataset was created.
            created_by (str): The user that created the dataset.
            description (str): The description of the dataset.
            function (Function): The function of the dataset.
            **kwargs: Additional keyword arguments.
        """
        self.name = name
        self.datastore = datastore
        self.created_on = created_on
        self.created_on_string = convert_timestamp_to_string(created_on)
        self.created_by = created_by
        self.description = description
        self.function = function
        self.kwargs = kwargs

    def __repr__(self) -> str:
        repr = (
            f"{self.__class__.__name__}(name={self.name!r},"
            f"datastore={self.datastore!r},"
            f"description={self.description!r},"
            f"created_on={self.created_on_string!r},"
            f"created_by={self.created_by!r}"
        )
        if self.function is not None:
            repr += f", function={self.function!r})"
        return repr

    def __str__(self) -> str:
        string = (
            f"Name: {self.name!s}, "
            f"datastore: {self.datastore!s}, "
            f"description: '{self.description!s}', "
            f"created on: {self.created_on_string!s}, "
            f"created by: {self.created_by!s}"
        )
        if self.function is not None:
            string += f", function: <{self.function!s}>"
        return string

    def __eq__(self, other) -> bool:
        if not isinstance(other, Dataset):
            return False
        return self.name == other.name and self.datastore == other.datastore


class Datastore:
    """
    This class represents a datastore in the TabsdataServer.

    Args:
        name (str): The name of the datastore.
        id (str): The id of the datastore.
        description (str): The description of the datastore.
        created_on (int): The timestamp when the datastore was created.
        created_by (str): The user that created the datastore.
        **kwargs: Additional keyword

    Attributes:
        created_on_string (str): The timestamp when the datastore was created as a
            string.
    """

    def __init__(
        self,
        name: str,
        description: str,
        created_on: int,
        created_by: str,
        **kwargs,
    ):
        """
        Initialize the Datastore object.

        Args:
            name (str): The name of the datastore.
            description (str): The description of the datastore.
            created_on (int): The timestamp when the datastore was created.
            created_by (str): The user that created the datastore.
            **kwargs: Additional keyword arguments.
        """
        self.name = name
        self.description = description
        self.created_on = created_on
        self.created_on_string = convert_timestamp_to_string(created_on)
        self.created_by = created_by
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r},"
            f"description={self.description!r},"
            f"created_on={self.created_on_string!r},"
            f"created_by={self.created_by!r})"
        )

    def __str__(self) -> str:
        return (
            f"Name: {self.name!r}, description: {self.description!r}, "
            f"created_on: {self.created_on_string!r}, created_by: {self.created_by!r}"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Datastore):
            return False
        return self.name == other.name


class ServerStatus:
    """
    This class represents the status of the TabsdataServer.

    Args:
        status (str): The status of the server.
        latency_as_nanos (int): The latency of the server in nanoseconds.
        **kwargs: Additional keyword arguments.
    """

    def __init__(self, status: str, latency_as_nanos: int, **kwargs):
        """
        Initialize the ServerStatus object.

        Args:
            status (str): The status of the server.
            latency_as_nanos (int): The latency of the server in nanoseconds.
            **kwargs: Additional keyword arguments.
        """
        self.status = status
        self.latency_as_nanos = latency_as_nanos
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(status={self.status!r},"
            f" latency_as_nanos={self.latency_as_nanos!r})"
        )

    def __str__(self) -> str:
        return f"Status: {self.status!r}, latency_as_nanos: {self.latency_as_nanos!r}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ServerStatus):
            return False
        return self.status == other.status


class User:
    """
    This class represents a user in the TabsdataServer.

    Args:
        name (str): The name of the user.
        full_name (str): The full name of the user.
        email (str): The email of the user.
        enabled (bool): Whether the user is enabled or not.
        **kwargs: Additional keyword arguments.
    """

    def __init__(self, name: str, full_name: str, email: str, enabled: bool, **kwargs):
        """
        Initialize the User object.

        Args:
            name (str): The name of the user.
            full_name (str): The full name of the user.
            email (str): The email of the user.
            enabled (bool): Whether the user is enabled or not.
            **kwargs: Additional keyword arguments.
        """
        self.name = name
        self.full_name = full_name
        self.email = email
        self.enabled = enabled
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r},"
            f"full_name={self.full_name!r},"
            f"email={self.email!r},enabled={self.enabled!r})"
        )

    def __str__(self) -> str:
        return (
            f"Name: {self.name!r}, full name: {self.full_name!r}, email: "
            f"{self.email!r}, enabled: {self.enabled!r}"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.name == other.name


class TabsdataServer:
    """
    This class represents the TabsdataServer.

    Args:
        url (str): The url of the server.
        username (str): The username of the user.
        password (str): The password of the user.
    """

    def __init__(self, url: str, username: str, password: str):
        """
        Initialize the TabsdataServer object.

        Args:
            url (str): The url of the server.
            username (str): The username of the user.
            password (str): The password of the user.
        """
        self.connection = obtain_connection(url, username, password)

    @property
    def datastores(self) -> List[Datastore]:
        """
        Get the list of datastores in the server. This list is obtained every time the
            property is accessed, so sequential accesses to this property in the same
            object might yield different results.

        Returns:
            List[Datastore]: The list of datastores in the server.
        """
        raw_datastores = self.connection.datastore_list().json().get("data")
        return [Datastore(**datastore) for datastore in raw_datastores]

    @property
    def execution_plans(self) -> List[ExecutionPlan]:
        """
        Get the list of execution plans in the server. This list is obtained every time
            the property is accessed, so sequential accesses to this property in the
            same object might yield different results.

        Returns:
            List[ExecutionPlan]: The list of execution plans in the server.
        """
        raw_execution_plans = self.connection.execution_plan_list().json().get("data")
        return [
            ExecutionPlan(**execution_plan) for execution_plan in raw_execution_plans
        ]

    @property
    def users(self) -> List[User]:
        """
        Get the list of users in the server. This list is obtained every time the
            property is accessed, so sequential accesses to this property in the same
            object might yield different results.

        Returns:
            List[User]: The list of users in the server.
        """
        raw_users = self.connection.users_list().json().get("data")
        return [User(**user) for user in raw_users]

    @property
    def status(self) -> ServerStatus:
        """
        Get the status of the server. This status is obtained every time the property is
            accessed, so sequential accesses to this property in the same object might
            yield different results.

        Returns:
            ServerStatus: The status of the server.
        """
        return ServerStatus(
            **self.connection.status_get().json().get("database_status")
        )

    def datastore_create(self, name: str, description: str = None) -> None:
        """
        Create a datastore in the server.

        Args:
            name (str): The name of the datastore.
            description (str, optional): The description of the datastore.

        Raises:
            APIServerError: If the datastore could not be created.
        """
        description = description or name
        self.connection.datastore_create(name, description)

    def datastore_delete(self, name: str) -> None:
        """
        Delete a datastore in the server.

        Args:
            name (str): The name of the datastore.

        Raises:
            APIServerError: If the datastore could not be deleted.
        """
        self.connection.datastore_delete(name)

    def datastore_get(self, name: str) -> Datastore:
        """
        Get a datastore in the server.

        Args:
            name (str): The name of the datastore.

        Returns:
            Datastore: The datastore.

        Raises:
            APIServerError: If the datastore could not be obtained.
        """
        return Datastore(**self.connection.datastore_get_by_name(name).json())

    def datastore_update(
        self, name: str, new_name=None, new_description: str = None
    ) -> None:
        """
        Update a datastore in the server.

        Args:
            name (str): The name of the datastore.
            new_name (str, optional): The new name of the datastore.
            new_description (str, optional): The new description of the datastore.

        Raises:
            APIServerError: If the datastore could not be updated.
        """
        self.connection.datastore_update(
            name, new_datastore_name=new_name, description=new_description
        )

    def user_create(
        self,
        name: str,
        password: str,
        full_name: str = None,
        email: str = None,
        enabled: bool = True,
    ) -> None:
        """
        Create a user in the server.

        Args:
            name (str): The name of the user.
            password (str): The password of the user.
            full_name (str, optional): The full name of the user.
            email (str, optional): The email of the user.
            enabled (bool, optional): Whether the user is enabled or not.

        Raises:
            APIServerError: If the user could not be created.
        """
        full_name = full_name or name
        self.connection.users_create(name, full_name, email, password, enabled)

    def user_delete(self, name: str) -> None:
        """
        Delete a user in the server.

        Args:
            name (str): The name of the user.

        Raises:
            APIServerError: If the user could not be deleted.
        """
        self.connection.users_delete(name)

    def user_get(self, name: str) -> User:
        """
        Get a user in the server.

        Args:
            name (str): The name of the user.

        Returns:
            User: The user.

        Raises:
            APIServerError: If the user could not be obtained.
        """
        return User(**self.connection.users_get_by_name(name).json())

    def user_update(
        self,
        name: str,
        full_name: str = None,
        email: str = None,
        enabled: bool = None,
    ) -> None:
        # TODO: Implement change password logic, for now only full name, email
        #  and disabled are updated
        """
        Update a user in the server.

        Args:
            name (str): The name of the user.
            full_name (str, optional): The full name of the user.
            email (str, optional): The email of the user.
            enabled (bool, optional): Whether the user is enabled or not.

        Raises:
            APIServerError: If the user could not be updated.
        """
        self.connection.users_update(
            name,
            full_name=full_name,
            email=email,
            enabled=enabled,
        )

    def dataset_create(
        self,
        datastore_name: str,
        function_path: str,
        description: str = None,
        path_to_bundle: str = None,
        requirements: str = None,
        local_packages: List[str] | str | None = None,
    ) -> None:
        """
        Create a dataset in the server.

        Args:
            datastore_name (str): The name of the datastore.
            function_path (str): The path to the function. It should be in the form of
                /path/to/file.py::function_name.
            description (str, optional): The description of the dataset.
            path_to_bundle (str, optional): The path that has to be bundled and sent
                to the server. If None, the folder containing the function will be
                bundled.
            requirements (str, optional): Path to a custom requirements.yaml file
                with the packages, python version and other information needed to
                create the Python environment for the function to run in the backend.
                If not provided, this information will be inferred from the current
                execution session.
            local_packages (List[str] | str, optional): A list of paths to local
                Python packages that need to be included in the bundle. Each path
                must exist and be a valid Python package that can be installed by
                running `pip install /path/to/package`.

        Raises:
            APIServerError: If the dataset could not be created.
        """

        temporary_directory = tempfile.TemporaryDirectory()
        (
            bundle_hash,
            tables,
            string_dependencies,
            trigger_by,
            function_snippet,
            context_location,
            dataset_name,
        ) = create_archive_and_hash(
            function_path,
            temporary_directory,
            path_to_bundle,
            requirements,
            local_packages,
        )

        description = description or dataset_name

        response = self.connection.dataset_create(
            datastore_name=datastore_name,
            dataset_name=dataset_name,
            description=description,
            bundle_hash=bundle_hash,
            tables=tables,
            dependencies=string_dependencies,
            trigger_by=trigger_by,
            function_snippet=function_snippet,
        )
        current_function_id = response.json().get("current_function_id")
        with open(context_location, "rb") as file:
            bundle = file.read()

        self.connection.dataset_upload_function_bundle(
            datastore_name=datastore_name,
            dataset_name=dataset_name,
            function_id=current_function_id,
            bundle=bundle,
        )

    def dataset_update(
        self,
        datastore_name: str,
        dataset_name: str,
        function_path: str,
        description: str,
        directory_to_bundle: str = None,
        requirements: str = None,
        local_packages: List[str] | str | None = None,
    ) -> None:
        """
        Update a dataset in the server.

        Args:
            datastore_name (str): The name of the datastore.
            dataset_name (str): The name of the dataset.
            function_path (str): The path to the function. It should be in the form of
                /path/to/file.py::function_name.
            description (str): The new description of the dataset.
            directory_to_bundle (str, optional): The path that has to be bundled and
                sent to the server. If None, the folder containing the function will be
                bundled.
            requirements (str, optional): Path to a custom requirements.yaml file
                with the packages, python version and other information needed to
                create the Python environment for the function to run in the backend.
                If not provided, this information will be inferred from the current
                execution session.
            local_packages (List[str] | str, optional): A list of paths to local
                Python packages that need to be included in the bundle. Each path
                must exist and be a valid Python package that can be installed by
                running `pip install /path/to/package`.

        Raises:
            APIServerError: If the dataset could not be updated.
        """
        temporary_directory = tempfile.TemporaryDirectory()
        (
            bundle_hash,
            tables,
            string_dependencies,
            trigger_by,
            function_snippet,
            context_location,
            new_dataset_name,
        ) = create_archive_and_hash(
            function_path,
            temporary_directory,
            directory_to_bundle,
            requirements,
            local_packages,
        )

        response = self.connection.dataset_update(
            datastore_name=datastore_name,
            dataset_name=dataset_name,
            new_dataset_name=new_dataset_name,
            description=description,
            bundle_hash=bundle_hash,
            tables=tables,
            dependencies=string_dependencies,
            trigger_by=trigger_by,
            function_snippet=function_snippet,
        )

        current_function_id = response.json().get("current_function_id")
        with open(context_location, "rb") as file:
            bundle = file.read()

        self.connection.dataset_upload_function_bundle(
            datastore_name=datastore_name,
            dataset_name=new_dataset_name or dataset_name,
            function_id=current_function_id,
            bundle=bundle,
        )

    def dataset_delete(self, datastore_name, dataset_name) -> None:
        """
        Delete a dataset in the server.

        Args:
            datastore_name (str): The name of the datastore.
            dataset_name (str): The name of the dataset.

        Raises:
            APIServerError: If the dataset could not be deleted.
        """
        self.connection.dataset_delete(datastore_name, dataset_name)

    def dataset_list_functions(self, datastore_name, dataset_name) -> List[Function]:
        """
        List the functions in a dataset.

        Args:
            datastore_name (str): The name of the datastore.
            dataset_name (str): The name of the dataset.

        Returns:
            List[Function]: The list of functions in the dataset.

        Raises:
            APIServerError: If the functions could not be listed.
        """
        raw_list_of_functions = (
            self.connection.dataset_list_functions(datastore_name, dataset_name)
            .json()
            .get("data")
        )
        return [Function(**function) for function in raw_list_of_functions]

    def dataset_trigger(self, datastore_name, dataset_name) -> requests.Response:
        """
        Trigger a dataset in the server.

        Args:
            datastore_name (str): The name of the datastore.
            dataset_name (str): The name of the dataset.

        Returns:
            requests.Response: The response of the trigger request.

        Raises:
            APIServerError: If the dataset could not be triggered.
        """
        return self.connection.dataset_execute(datastore_name, dataset_name)

    def dataset_get(self, datastore_name, dataset_name) -> Dataset:
        """
        Get a dataset in the server.

        Args:
            datastore_name (str): The name of the datastore.
            dataset_name (str): The name of the dataset.

        Returns:
            Dataset: The dataset.

        Raises:
            APIServerError: If the dataset could not be obtained.
        """
        dataset_definition = self.connection.dataset_show_current_function(
            datastore_name, dataset_name
        ).json()
        dataset_definition["datastore"] = datastore_name
        function_definition = {}
        function_definition_keys = [
            "trigger_with_names",
            "tables",
            "dependencies_with_names",
        ]
        for function_definition_key in function_definition_keys:
            function_definition[function_definition_key] = dataset_definition.pop(
                function_definition_key
            )
        function = Function(**function_definition)
        dataset_definition["function"] = function
        return Dataset(**dataset_definition)

    def datastore_list_dataset(self, datastore_name) -> List[Dataset]:
        """
        List the datasets in a datastore.

        Args:
            datastore_name (str): The name of the datastore.

        Returns:
            List[Dataset]: The list of datasets in the datastore.

        Raises:
            APIServerError: If the datasets could not be listed.
        """
        raw_list_of_datasets = (
            self.connection.dataset_in_datastore_list(datastore_name).json().get("data")
        )
        return [Dataset(**dataset) for dataset in raw_list_of_datasets]


def calculate_file_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def dynamic_import_function_from_path(path: str) -> DatasetFunction:
    """
    Dynamically import a function from a path in the form of 'path::function_name'.
    :param path:
    :return:
    """
    file_path, function_name = path.split("::")
    sys.path.insert(0, os.path.dirname(file_path))
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    function = getattr(module, function_name)
    return function


def create_archive_and_hash(
    function_path,
    temporary_directory,
    path_to_bundle=None,
    requirements=None,
    local_packages=None,
):
    function = dynamic_import_function_from_path(function_path)
    dataset_name: str = function.dataset_name
    function_output = function.output
    tables = (
        function_output._table_list if isinstance(function_output, TableOutput) else []
    )
    dependencies: List[URI] = (
        function.input._uri_list if isinstance(function.input, TableInput) else []
    )
    string_dependencies: List[str] = [
        dependency.to_string() for dependency in dependencies
    ]
    trigger = function.trigger_by
    trigger_by = trigger.to_string() if isinstance(trigger, URI) else trigger
    try:
        function_snippet = inspect.getsource(function.original_function)
    except OSError:
        function_snippet = "Function source code not available"
    context_location = create_bundle_archive(
        function,
        save_location=temporary_directory.name,
        path_to_code=path_to_bundle,
        requirements=requirements,
        local_packages=local_packages,
    )
    bundle_hash = calculate_file_sha256(context_location)
    return (
        bundle_hash,
        tables,
        string_dependencies,
        trigger_by,
        function_snippet,
        context_location,
        dataset_name,
    )


def convert_timestamp_to_string(timestamp: int | None) -> str:
    if not timestamp:
        return str(timestamp)
    return str(
        datetime.datetime.fromtimestamp(timestamp / 1e3, datetime.UTC).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )
