#
# Copyright 2024 Tabs Data Inc.
#

import datetime
import os
from typing import List

import rich_click as click
from rich.console import Console
from rich.table import Table

from tabsdatasdk.cli.cli_utils import (
    DEFAULT_TABSDATA_DIRECTORY,
    MutuallyExclusiveOption,
    beautify_list,
    logical_prompt,
)
from tabsdatasdk.uri import build_uri_object


@click.group()
@click.pass_context
def dataset(ctx: click.Context):
    """Dataset management commands"""
    if not ctx.obj["tabsdataserver"]:
        raise click.ClickException("No credentials found. Please login first.")


@dataset.command()
@click.option(
    "--datastore",
    "-d",
    cls=MutuallyExclusiveOption,
    help="Name of the datastore to which the dataset belongs.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--uri",
    "-u",
    cls=MutuallyExclusiveOption,
    help="URI of the datastore where the dataset will be created.",
    mutually_exclusive=["datastore"],
)
@click.option("--description", help="Description of the dataset.")
@click.option(
    "--function-path",
    "-f",
    help=(
        "Path to the function file. Must be of the form "
        "'/path/to/file.py::function_name'. Will be prompted "
        "for it if not provided."
    ),
)
@click.option(
    "--directory-to-bundle",
    "-p",
    help=(
        "Path to the directory that should be stored in the bundle for "
        "execution in the backed. If not provided, the folder where the "
        "function file is will be used."
    ),
)
@click.option(
    "--requirements-file",
    "-r",
    help=(
        "Path to the requirements file. If not provided, the requirements file will "
        "be generated based on your current Python environment."
    ),
)
@click.option(
    "--local-package",
    "-l",
    multiple=False,
    help="Path to a local package to include in the bundle.",
)
@click.pass_context
def create(
    ctx: click.Context,
    datastore: str,
    uri: str,
    description: str,
    function_path: str,
    directory_to_bundle: str,
    requirements_file: str,
    local_package: List[str],
):
    """Create a new dataset"""
    click.echo("Creating a new dataset")
    click.echo("-" * 10)
    if not uri:
        datastore = datastore or logical_prompt(
            ctx, "Name of the datastore to which the dataset belongs"
        )
    else:
        uri_obj = build_uri_object(uri)
        datastore = uri_obj.datastore
    description = description or logical_prompt(
        ctx, "Description of the dataset", default_value=""
    )
    function_path = function_path or logical_prompt(
        ctx,
        "Path to the function file. "
        "Must be of the form "
        "'/path/to/file.py::function_name'",
    )
    try:
        ctx.obj["tabsdataserver"].dataset_create(
            datastore,
            function_path,
            description,
            directory_to_bundle,
            requirements_file,
            local_package,
        )
        click.echo("Dataset created successfully")
    except Exception as e:
        raise click.ClickException(f"Failed to create dataset: {e}")


@dataset.command()
@click.option(
    "--name",
    "-n",
    cls=MutuallyExclusiveOption,
    help="Name of the dataset to be deleted.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--datastore",
    "-d",
    cls=MutuallyExclusiveOption,
    help="Name of the datastore to which the dataset belongs.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--uri",
    "-u",
    cls=MutuallyExclusiveOption,
    help=(
        "URI of the dataset to be deleted. Must be of the form"
        " 'td:///datastore_name/dataset_name'."
    ),
    mutually_exclusive=["name", "datastore"],
)
@click.option(
    "--confirm",
    help="Write 'delete' to confirm deletion. Will be prompted for it if not provided.",
)
@click.pass_context
def delete(ctx: click.Context, name: str, datastore: str, uri: str, confirm: str):
    """Delete a dataset"""
    click.echo(f"Deleting dataset '{name}' in datastore '{datastore}'")
    click.echo("-" * 10)
    if not uri:
        name = name or logical_prompt(ctx, "Name of the dataset to be deleted")
        datastore = datastore or logical_prompt(
            ctx, "Name of the datastore to which the dataset belongs"
        )
    else:
        uri_obj = build_uri_object(uri)
        name = uri_obj.dataset
        datastore = uri_obj.datastore
        if not name or not datastore:
            raise click.ClickException(
                "The URI provided does not point to a "
                "dataset. Please check that the URI is "
                "correct and try again. The URI should be "
                "of the form 'td:///datastore_name/dataset_name'."
            )
    confirm = confirm or logical_prompt(ctx, "Please type 'delete' to confirm deletion")
    if confirm != "delete":
        raise click.ClickException(
            "Deletion not confirmed. The confirmation word is 'delete'."
        )
    try:
        ctx.obj["tabsdataserver"].dataset_delete(datastore, name)
        click.echo("Dataset deleted successfully")
    except Exception as e:
        raise click.ClickException(f"Failed to delete dataset: {e}")


@dataset.command()
@click.option(
    "--name",
    "-n",
    cls=MutuallyExclusiveOption,
    help="Name of the dataset to be displayed.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--datastore",
    "-d",
    cls=MutuallyExclusiveOption,
    help="Name of the datastore to which the dataset belongs.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--uri",
    "-u",
    cls=MutuallyExclusiveOption,
    help=(
        "URI of the dataset to be created. Must be of the form"
        " 'td:///datastore_name/dataset_name'."
    ),
    mutually_exclusive=["name", "datastore"],
)
@click.option(
    "--show-versions",
    is_flag=True,
    help=(
        "Show the different versions that have existed of the datastore, newest first."
    ),
)
@click.pass_context
def display(
    ctx: click.Context, name: str, datastore: str, uri: str, show_versions: bool
):
    """Display a dataset"""
    if not uri:
        name = name or logical_prompt(ctx, "Name of the dataset to be displayed")
        datastore = datastore or logical_prompt(
            ctx, "Name of the datastore to which the dataset belongs"
        )
    else:
        uri_obj = build_uri_object(uri)
        name = uri_obj.dataset
        datastore = uri_obj.datastore
        if not name or not datastore:
            raise click.ClickException(
                "The URI provided does not point to a "
                "dataset. Please check that the URI is "
                "correct and try again. The URI should be "
                "of the form 'td:///datastore_name/dataset_name'."
            )
    try:
        if show_versions:
            functions = ctx.obj["tabsdataserver"].dataset_list_functions(
                datastore, name
            )

            table = Table(
                title=f"History of dataset '{name}' in datastore '{datastore}'"
            )
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Description")
            table.add_column("Created on")
            table.add_column("Created by")
            table.add_column("Dependency URIs")
            table.add_column("Trigger URI")
            table.add_column("Tables")

            for function in functions:
                table.add_row(
                    function.name,
                    function.description,
                    function.created_on_string,
                    function.created_by,
                    beautify_list(function.dependencies_with_names),
                    str(function.trigger_with_names),
                    beautify_list(function.tables),
                )

            click.echo()
            console = Console()
            console.print(table)
            click.echo(f"Number versions: {len(functions)}")
            click.echo()
        else:
            dataset = ctx.obj["tabsdataserver"].dataset_get(datastore, name)

            table = Table(title=f"Dataset '{name}' in datastore '{datastore}'")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Description")
            table.add_column("Created on")
            table.add_column("Created by")
            table.add_column("Dependency URIs")
            table.add_column("Trigger URI")
            table.add_column("Tables")

            table.add_row(
                dataset.name,
                dataset.description,
                dataset.created_on_string,
                dataset.created_by,
                beautify_list(dataset.function.dependencies_with_names),
                str(dataset.function.trigger_with_names),
                beautify_list(dataset.function.tables),
            )

            click.echo()
            console = Console()
            console.print(table)
            click.echo()
    except Exception as e:
        raise click.ClickException(f"Failed to display dataset: {e}")


@dataset.command()
@click.option(
    "--datastore",
    "-d",
    cls=MutuallyExclusiveOption,
    help="Name of the datastore to which the dataset belongs.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--uri",
    "-u",
    cls=MutuallyExclusiveOption,
    help="URI of the dataset to be created.",
    mutually_exclusive=["datastore"],
)
@click.pass_context
def list(ctx: click.Context, datastore: str, uri: str):
    """List all datasets in a datastore"""
    if not uri:
        datastore = datastore or logical_prompt(
            ctx, "Name of the datastore to which the dataset belongs"
        )
    else:
        datastore = build_uri_object(uri).datastore
        if not datastore:
            raise click.ClickException(
                "The URI provided does not point to a "
                "datastore. Please check that the URI is "
                "correct and try again. The URI should be "
                "of the form 'td:///datastore_name'."
            )
    try:
        list_of_datasets = ctx.obj["tabsdataserver"].datastore_list_dataset(datastore)

        table = Table(title=f"Datasets in datastore '{datastore}'")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description")
        table.add_column("Created on")
        table.add_column("Created by")

        for dataset in list_of_datasets:
            table.add_row(
                dataset.name,
                dataset.description,
                dataset.created_on_string,
                dataset.created_by,
            )

        click.echo()
        console = Console()
        console.print(table)
        click.echo(
            f"Number of datasets in datastore '{datastore}': {len(list_of_datasets)}"
        )
        click.echo()

    except Exception as e:
        raise click.ClickException(f"Failed to list datasets: {e}")


@dataset.command()
@click.option(
    "--name",
    "-n",
    cls=MutuallyExclusiveOption,
    help="Name of the dataset to be displayed.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--datastore",
    "-d",
    cls=MutuallyExclusiveOption,
    help="Name of the datastore to which the dataset belongs.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--uri",
    "-u",
    cls=MutuallyExclusiveOption,
    help=(
        "URI of the dataset to be created. Must be of the form"
        " 'td:///datastore_name/dataset_name'."
    ),
    mutually_exclusive=["name", "datastore"],
)
@click.pass_context
def trigger(ctx: click.Context, name: str, datastore: str, uri: str):
    """Trigger a dataset"""
    if not uri:
        name = name or logical_prompt(ctx, "Name of the dataset to be triggered")
        datastore = datastore or logical_prompt(
            ctx, "Name of the datastore to which the dataset belongs"
        )
    else:
        uri_obj = build_uri_object(uri)
        name = uri_obj.dataset
        datastore = uri_obj.datastore
        if not name or not datastore:
            raise click.ClickException(
                "The URI provided does not point to a "
                "dataset. Please check that the URI is "
                "correct and try again. The URI should be "
                "of the form 'td:///datastore_name/dataset_name'."
            )
    click.echo(f"Triggering dataset '{name}' in datastore '{datastore}'")
    click.echo("-" * 10)
    try:
        response = ctx.obj["tabsdataserver"].dataset_trigger(datastore, name)
        click.echo("Dataset triggered successfully")
        dot = response.json().get("dot")
        if dot:
            folder = os.path.join(DEFAULT_TABSDATA_DIRECTORY, "dot")
            os.makedirs(folder, exist_ok=True)
            current_timestamp = int(
                datetime.datetime.now().replace(microsecond=0).timestamp()
            )
            file_name = f"{datastore}-{name}-{current_timestamp}.dot"
            full_path = os.path.join(folder, file_name)
            with open(full_path, "w") as f:
                f.write(dot)
            click.echo(f"Plan DOT at path: {full_path}")
        else:
            click.echo("No DOT returned")
    except Exception as e:
        raise click.ClickException(f"Failed to trigger dataset: {e}")


@dataset.command()
@click.option(
    "--name",
    "-n",
    cls=MutuallyExclusiveOption,
    help="Name of the dataset to be updated.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--datastore",
    "-d",
    cls=MutuallyExclusiveOption,
    help="Name of the datastore to which the dataset belongs.",
    mutually_exclusive=["uri"],
)
@click.option(
    "--uri",
    "-u",
    cls=MutuallyExclusiveOption,
    help="URI of the dataset to be updated.",
    mutually_exclusive=["name", "datastore"],
)
@click.option("--description", help="Description of the dataset.")
@click.option(
    "--function-path",
    "-f",
    help=(
        "Path to the function file. Must be of the form "
        "'/path/to/file.py::function_name'. Will be prompted "
        "for it if not provided."
    ),
)
@click.option(
    "--directory-to-bundle",
    "-p",
    help=(
        "Path to the directory that should be stored in the bundle for "
        "execution in the backed. If not provided, the folder where the "
        "function file is will be used."
    ),
)
@click.option(
    "--requirements-file",
    "-r",
    help=(
        "Path to the requirements file. If not provided, the requirements file will "
        "be generated based on your current Python environment."
    ),
)
@click.option(
    "--local-package",
    "-l",
    multiple=True,
    help="Path to a local package to include in the bundle.",
)
@click.pass_context
def update(
    ctx: click.Context,
    name: str,
    datastore: str,
    uri: str,
    description: str,
    function_path: str,
    directory_to_bundle: str,
    requirements_file: str,
    local_package: List[str],
):
    """Update a dataset"""
    if not uri:
        name = name or logical_prompt(ctx, "Name of the dataset to be updated")
        datastore = datastore or logical_prompt(
            ctx, "Name of the datastore to which the dataset belongs"
        )
    else:
        uri_obj = build_uri_object(uri)
        name = uri_obj.dataset
        datastore = uri_obj.datastore
    description = description or logical_prompt(
        ctx, "New description of the dataset", default_value=""
    )
    function_path = function_path or logical_prompt(
        ctx,
        "Path to the function file. "
        "Must be of the form "
        "'/path/to/file.py::function_name'",
    )
    click.echo(f"Updating dataset '{name}' in datastore '{datastore}'")
    click.echo("-" * 10)
    try:
        ctx.obj["tabsdataserver"].dataset_update(
            datastore_name=datastore,
            dataset_name=name,
            function_path=function_path,
            description=description,
            directory_to_bundle=directory_to_bundle,
            requirements=requirements_file,
            local_packages=local_package,
        )
        click.echo("Datastore updated successfully")
    except Exception as e:
        raise click.ClickException(f"Failed to update datastore: {e}")
