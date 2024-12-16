#
# Copyright 2024 Tabs Data Inc.
#


import rich_click as click
from rich.console import Console
from rich.table import Table

from tabsdatasdk.cli.cli_utils import logical_prompt


@click.group()
@click.pass_context
def datastore(ctx: click.Context):
    """Datastore management commands"""
    if not ctx.obj["tabsdataserver"]:
        raise click.ClickException("No credentials found. Please login first.")


@datastore.command()
@click.argument("name")
@click.option("--description", help="Description of the datastore.")
@click.pass_context
def create(
    ctx: click.Context,
    name: str,
    description: str,
):
    """Create a new datastore"""
    click.echo("Creating a new datastore")
    click.echo("-" * 10)
    description = description or logical_prompt(
        ctx, "Description of the datastore", default_value=name
    )
    try:
        ctx.obj["tabsdataserver"].datastore_create(name, description)
        click.echo("Datastore created successfully")
    except Exception as e:
        raise click.ClickException(f"Failed to create datastore: {e}")


@datastore.command()
@click.argument("name")
@click.option(
    "--confirm",
    help="Write 'delete' to confirm deletion. Will be prompted for it if not provided.",
)
@click.pass_context
def delete(ctx: click.Context, name: str, confirm: str):
    """Delete a datastore by name"""
    click.echo(f"Deleting datastore: {name}")
    click.echo("-" * 10)
    confirm = confirm or logical_prompt(ctx, "Please type 'delete' to confirm deletion")
    if confirm != "delete":
        raise click.ClickException(
            "Deletion not confirmed. The confirmation word is 'delete'."
        )
    try:
        ctx.obj["tabsdataserver"].datastore_delete(name)
        click.echo("Datastore deleted successfully")
    except Exception as e:
        raise click.ClickException(f"Failed to delete datastore: {e}")


@datastore.command()
@click.argument("name")
@click.pass_context
def display(ctx: click.Context, name: str):
    """Display a datastore by name"""
    try:
        datastore = ctx.obj["tabsdataserver"].datastore_get(name)
        click.echo(datastore)

        table = Table(title=f"Datastore '{name}'")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description")
        table.add_column("Created on")
        table.add_column("Created by")

        table.add_row(
            datastore.name,
            datastore.description,
            datastore.created_on_string,
            datastore.created_by,
        )

        click.echo()
        console = Console()
        console.print(table)
        click.echo()
    except Exception as e:
        raise click.ClickException(f"Failed to display datastore: {e}")


@datastore.command()
@click.pass_context
def list(ctx: click.Context):
    """List all datastores"""
    try:
        list_of_datastores = ctx.obj["tabsdataserver"].datastores

        table = Table(title="Datastores")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description")
        table.add_column("Created on")
        table.add_column("Created by")

        for datastore in list_of_datastores:
            table.add_row(
                datastore.name,
                datastore.description,
                datastore.created_on_string,
                datastore.created_by,
            )

        click.echo()
        console = Console()
        console.print(table)
        click.echo(f"Number of datastores: {len(list_of_datastores)}")
        click.echo()
    except Exception as e:
        raise click.ClickException(f"Failed to list datastores: {e}")


@datastore.command()
@click.argument("name")
@click.option("--new-name", "-n", help="New name for the datastore.")
@click.option("--description", help="New description for the datastore.")
@click.pass_context
def update(
    ctx: click.Context,
    name: str,
    new_name: str,
    description: str,
):
    """Update a datastore by name"""
    click.echo(f"Updating datastore: {name}")
    click.echo("-" * 10)
    try:
        ctx.obj["tabsdataserver"].datastore_update(
            name, new_name=new_name, new_description=description
        )
        click.echo("Datastore updated successfully")
    except Exception as e:
        raise click.ClickException(f"Failed to update datastore: {e}")
