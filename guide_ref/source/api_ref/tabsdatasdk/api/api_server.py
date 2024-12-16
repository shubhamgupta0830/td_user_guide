#
# Copyright 2024 Tabs Data Inc.
#

import json
from urllib.parse import urlparse

import requests

DEFAULT_APISERVER_PORT = "2457"
HTTP_PROTOCOL = "http://"
PORT_SEPARATOR = ":"


class APIServerError(Exception):

    def __init__(self, dictionary: dict):
        self.code = dictionary.get("code")
        self.error = dictionary.get("error")
        self.error_description = dictionary.get("error_description")
        super().__init__(
            self.error_description if self.error_description else "Unknown error"
        )


def process_url(url: str) -> str:
    """
    A helper function to process the url string. It adds the protocol and the
        default port if missing
    """
    if not url.startswith(HTTP_PROTOCOL):
        url = HTTP_PROTOCOL + url
    parsed_url = urlparse(url)
    if not parsed_url.port:
        url = url + PORT_SEPARATOR + DEFAULT_APISERVER_PORT
    return url


class APIServer:

    def __init__(self, url: str):
        url = process_url(url)
        self.url = url
        self.bearer_token = None
        self.refresh_token = None

    @property
    def authentication_header(self):
        return {"Authorization": f"Bearer {self.bearer_token}"}

    def get(self, path, params=None):

        return requests.get(
            self.url + path, headers=self.authentication_header, params=params
        )

    def post(self, path, data):
        return requests.post(
            self.url + path, json=data, headers=self.authentication_header
        )

    def post_binary(self, path, data):
        headers = {"Content-Type": "application/octet-stream"}
        headers.update(self.authentication_header)
        return requests.post(self.url + path, data=data, headers=headers)

    def delete(self, path):
        return requests.delete(self.url + path, headers=self.authentication_header)

    def _store_in_file(self, file_path: str):
        with open(file_path, "w") as file:
            json.dump(
                {
                    "url": self.url,
                    "bearer_token": self.bearer_token,
                    "refresh_token": self.refresh_token,
                },
                file,
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.url!r})"

    def __str__(self):
        return self.url

    def __eq__(self, other):
        if not isinstance(other, APIServer):
            return False
        return self.url == other.url

    def raise_for_status_or_return(
        self, raise_for_status: bool, response: requests.Response
    ) -> requests.Response:
        if raise_for_status:
            return self.raise_for_status(response)
        else:
            return response

    def authentication_access(self, name: str, password: str):
        endpoint = "/auth/access"
        data = {"name": name, "password": password}
        response = self.post(endpoint, data)
        if response.status_code == 200:
            self.bearer_token = response.json()["access_token"]
            self.refresh_token = response.json()["refresh_token"]
            return response
        else:
            raise APIServerError(response.json())

    def authentication_refresh(self):
        endpoint = "/auth/refresh"
        data = {"refresh_token": self.refresh_token}
        response = self.post(endpoint, data)
        if response.status_code == 200:
            self.bearer_token = response.json()["access_token"]
            self.refresh_token = response.json()["refresh_token"]
            return response
        else:
            raise APIServerError(response.json())

    def dataset_create(
        self,
        datastore_name: str,
        dataset_name: str,
        description: str,
        bundle_hash: str,
        tables: list[str],
        dependencies: list[str],
        trigger_by: str | None,
        function_snippet: str,
        raise_for_status: bool = True,
    ):
        endpoint = f"/datastores/{datastore_name}/datasets"

        data = {
            "name": dataset_name,
            "description": description,
            "bundle_hash": bundle_hash,
            "tables": tables,
            "dependencies": dependencies,
            "trigger_by": trigger_by,
            "function_snippet": function_snippet,
        }
        response = self.post(endpoint, data)
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_delete(
        self, datastore_name: str, dataset_name: str, raise_for_status: bool = True
    ):
        return
        # TODO: Implement this method once the API is ready
        endpoint = f"/datastores/{datastore_name}/datasets/{dataset_name}"
        response = self.delete(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_execute(
        self, datastore_name: str, dataset_name: str, raise_for_status: bool = True
    ):
        endpoint = f"/datastores/{datastore_name}/datasets/{dataset_name}/execute"
        response = self.post(endpoint, {})
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_get(
        self, datastore_name: str, dataset_name: str, raise_for_status: bool = True
    ):
        endpoint = f"/datastores/{datastore_name}/datasets/{dataset_name}"
        response = self.get(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_in_datastore_list(
        self,
        datastore_name: str,
        offset: int = None,
        len: int = None,
        filter: str = None,
        order_by: str = None,
        raise_for_status: bool = True,
    ):
        endpoint = f"/datastores/{datastore_name}/datasets"
        params = self.get_params_dict(
            ["offset", "len", "filter", "order_by"], [offset, len, filter, order_by]
        )
        response = self.get(endpoint, params=params)
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_list_functions(
        self,
        datastore_name: str,
        dataset_name: str,
        offset: int = None,
        len: int = None,
        filter: str = None,
        order_by: str = None,
        raise_for_status: bool = True,
    ):
        endpoint = f"/datastores/{datastore_name}/datasets/{dataset_name}/functions"
        params = self.get_params_dict(
            ["offset", "len", "filter", "order_by"], [offset, len, filter, order_by]
        )
        response = self.get(endpoint, params=params)
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_show_current_function(
        self, datastore_name: str, dataset_name: str, raise_for_status: bool = True
    ):
        endpoint = f"/datastores/{datastore_name}/datasets/{dataset_name}/function"
        response = self.get(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_update(
        self,
        datastore_name: str,
        dataset_name: str,
        new_dataset_name: str = None,
        description: str = None,
        bundle_hash: str = None,
        tables: list[str] = None,
        dependencies: list[str] = None,
        trigger_by: str = None,
        function_snippet: str = None,
        raise_for_status: bool = True,
    ):
        endpoint = f"/datastores/{datastore_name}/datasets/{dataset_name}"

        data = self.get_params_dict(
            [
                "name",
                "description",
                "bundle_hash",
                "tables",
                "dependencies",
                "trigger_by",
                "function_snippet",
            ],
            [
                new_dataset_name,
                description,
                bundle_hash,
                tables,
                dependencies,
                trigger_by,
                function_snippet,
            ],
        )
        response = self.post(endpoint, data)
        return self.raise_for_status_or_return(raise_for_status, response)

    def dataset_upload_function_bundle(
        self,
        datastore_name: str,
        dataset_name: str,
        function_id: str,
        bundle: bytes,
        raise_for_status: bool = True,
    ):
        endpoint = (
            f"/datastores/{datastore_name}/datasets/"
            f"{dataset_name}/function/{function_id}"
        )
        response = self.post_binary(endpoint, data=bundle)
        return self.raise_for_status_or_return(raise_for_status, response)

    def datastore_create(
        self, name: str, description: str, raise_for_status: bool = True
    ):
        endpoint = "/datastores"
        data = {"name": name, "description": description}
        response = self.post(endpoint, data)
        return self.raise_for_status_or_return(raise_for_status, response)

    def datastore_delete(self, datastore_name: str, raise_for_status: bool = True):
        endpoint = f"/datastores/{datastore_name}"
        response = self.delete(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def datastore_get_by_name(self, datastore_name: str, raise_for_status: bool = True):
        endpoint = f"/datastores/{datastore_name}"
        response = self.get(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def datastore_list(
        self,
        offset: int = None,
        len: int = None,
        filter: str = None,
        order_by: str = None,
        raise_for_status: bool = True,
    ):
        endpoint = "/datastores"

        params = self.get_params_dict(
            ["offset", "len", "filter", "order_by"], [offset, len, filter, order_by]
        )
        response = self.get(endpoint, params=params)
        return self.raise_for_status_or_return(raise_for_status, response)

    def datastore_update(
        self,
        datastore_name: str,
        new_datastore_name: str = None,
        description: str = None,
        raise_for_status: bool = True,
    ):
        endpoint = f"/datastores/{datastore_name}"
        data = self.get_params_dict(
            ["name", "description"], [new_datastore_name, description]
        )
        response = self.post(endpoint, data)
        return self.raise_for_status_or_return(raise_for_status, response)

    def execution_plan_list(
        self,
        offset: int = None,
        len: int = None,
        filter: str = None,
        order_by: str = None,
        raise_for_status: bool = True,
    ):
        endpoint = "/execution_plans"

        params = self.get_params_dict(
            ["offset", "len", "filter", "order_by"], [offset, len, filter, order_by]
        )
        response = self.get(endpoint, params)
        return self.raise_for_status_or_return(raise_for_status, response)

    def status_get(self, raise_for_status: bool = True):
        endpoint = "/status"
        response = self.get(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def table_get_by_id(self, table_id: str, raise_for_status: bool = True):
        endpoint = f"/tables/{table_id}"
        response = self.get(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def table_list_all(self, raise_for_status: bool = True):
        endpoint = "/tables"
        response = self.get(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def users_create(
        self,
        name: str,
        full_name: str,
        email: str,
        password: str,
        enabled: bool,
        raise_for_status: bool = True,
    ):
        endpoint = "/users"
        data = {
            "name": name,
            "full_name": full_name,
            "email": email,
            "password": password,
            "enabled": enabled,
        }
        response = self.post(endpoint, data)
        return self.raise_for_status_or_return(raise_for_status, response)

    def users_delete(self, name: str, raise_for_status: bool = True):
        endpoint = f"/users/{name}"
        response = self.delete(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def users_get_by_name(self, name: str, raise_for_status: bool = True):
        endpoint = f"/users/{name}"
        response = self.get(endpoint)
        return self.raise_for_status_or_return(raise_for_status, response)

    def users_list(
        self,
        offset: int = None,
        len: int = None,
        filter: str = None,
        order_by: str = None,
        raise_for_status: bool = True,
    ):
        endpoint = "/users"

        params = self.get_params_dict(
            ["offset", "len", "filter", "order_by"], [offset, len, filter, order_by]
        )
        response = self.get(endpoint, params)
        return self.raise_for_status_or_return(raise_for_status, response)

    def users_update(
        self,
        name: str,
        full_name: str = None,
        email: str = None,
        old_password: str = None,
        new_password: str = None,
        force_password_change: bool = False,
        enabled: bool = None,
        raise_for_status: bool = True,
    ):
        endpoint = f"/users/{name}"
        data = self.get_params_dict(
            ["full_name", "email", "enabled"], [full_name, email, enabled]
        )
        if old_password and new_password:
            data["password"] = {
                "Change": {"old_password": old_password, "new_password": new_password}
            }
        elif force_password_change:
            data["password"] = {"ForceChange": {"temporary_password": new_password}}
        response = self.post(endpoint, data)
        return self.raise_for_status_or_return(raise_for_status, response)

    @staticmethod
    def raise_for_status(response: requests.Response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise APIServerError(response.json())
        else:
            return response

    @staticmethod
    def get_params_dict(names: list, values: list) -> dict:
        return {name: value for name, value in zip(names, values) if value is not None}


def obtain_connection(url: str, name: str, password: str) -> APIServer:
    connection = APIServer(url)
    connection.authentication_access(name, password)
    return connection
