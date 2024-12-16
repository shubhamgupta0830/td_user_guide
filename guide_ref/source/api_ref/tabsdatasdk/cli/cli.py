#
# Copyright 2024 Tabs Data Inc.
#

import json
import os

import rich_click as click

from tabsdatasdk.api.api_server import APIServer, obtain_connection
from tabsdatasdk.api.tabsdata_server import TabsdataServer
from tabsdatasdk.cli.cli_utils import DEFAULT_TABSDATA_DIRECTORY, logical_prompt
from tabsdatasdk.cli.dataset_group import dataset
from tabsdatasdk.cli.datastore_group import datastore
from tabsdatasdk.cli.execution_plan_group import execution_plan
from tabsdatasdk.cli.user_group import user

CONNECTION_FILE = "connection.json"


@click.group()
@click.version_option()
@click.option(
    "--no-prompt",
    is_flag=True,
    help=(
        "Disable all prompts. If a prompt is required for proper execution, "
        "the command will fail."
    ),
)
@click.pass_context
def cli(ctx: click.Context, no_prompt: bool):
    """Main CLI for the Tabs Data SDK"""
    os.makedirs(DEFAULT_TABSDATA_DIRECTORY, exist_ok=True)
    ctx.obj = {"tabsdata_directory": DEFAULT_TABSDATA_DIRECTORY, "no_prompt": no_prompt}
    try:
        credentials = json.load(
            open(os.path.join(DEFAULT_TABSDATA_DIRECTORY, CONNECTION_FILE))
        )
        connection = APIServer(credentials.get("url"))
        connection.refresh_token = credentials.get("refresh_token")
        connection.bearer_token = credentials.get("bearer_token")
        tabsdata_server = TabsdataServer.__new__(TabsdataServer)
        tabsdata_server.connection = connection
    except FileNotFoundError:
        tabsdata_server = None
    ctx.obj["tabsdataserver"] = tabsdata_server


cli.add_command(dataset)
cli.add_command(datastore)
cli.add_command(execution_plan)
cli.add_command(user)


@cli.command()
@click.argument("server-url")
@click.option(
    "--username",
    "-u",
    help="Username for the TabsData Server. Will be prompted for it if not provided.",
)
@click.option(
    "--password",
    "-p",
    help=(
        "Password for the TabsData Server. It is discouraged to send the password as a "
        "plain argument, it should be either sent as the value of an environment "
        "variable or written through the prompt. Will be prompted for it if not "
        "provided."
    ),
)
@click.pass_context
def login(ctx: click.Context, server_url: str, username: str, password: str):
    """Login to the TabsData Server"""
    username = username or logical_prompt(ctx, "Username for the TabsData Server")
    password = password or logical_prompt(
        ctx,
        "Password for the TabsData Server",
        hide_input=True,
    )
    try:
        connection = obtain_connection(server_url, username, password)
    except Exception as e:
        raise click.ClickException(f"Failed to login: {e}")
    connection._store_in_file(
        os.path.join(ctx.obj["tabsdata_directory"], CONNECTION_FILE)
    )
    click.echo("Login successful.")


@cli.command()
@click.pass_context
def logout(ctx: click.Context):
    """Logout from the TabsData Server"""
    try:
        os.remove(os.path.join(ctx.obj["tabsdata_directory"], CONNECTION_FILE))
    except FileNotFoundError:
        click.echo("No credentials found.")
    else:
        click.echo("Logout successful.")


@cli.command()
@click.pass_context
def status(ctx: click.Context):
    """Check the status of the server"""
    """Dataset management commands"""
    if not ctx.obj["tabsdataserver"]:
        raise click.ClickException("No credentials found. Please login first.")
    click.echo("Obtaining server status")
    click.echo("-" * 10)
    try:
        current_status = ctx.obj["tabsdataserver"].status
        click.echo(str(current_status))
    except Exception as e:
        raise click.ClickException(f"Failed to get status: {e}")


if __name__ == "__main__":
    cli()
