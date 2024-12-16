#
# Copyright 2024 Tabs Data Inc.
#


import rich_click as click
from rich.console import Console
from rich.table import Table


@click.group()
@click.pass_context
def execution_plan(ctx: click.Context):
    """User management commands"""
    if not ctx.obj["tabsdataserver"]:
        raise click.ClickException("No credentials found. Please login first.")


@execution_plan.command()
@click.pass_context
def list(ctx: click.Context):
    """List all execution plans"""
    try:
        list_of_plans = ctx.obj["tabsdataserver"].execution_plans

        table = Table(title="Execution plans")
        table.add_column("Datastore", style="cyan", no_wrap=True)
        table.add_column("Dataset", style="cyan", no_wrap=True)
        table.add_column("Status")
        table.add_column("Triggered on")
        table.add_column("Triggered by")
        table.add_column("Started on")
        table.add_column("Ended on")

        for plan in list_of_plans:
            table.add_row(
                plan.datastore,
                plan.dataset,
                plan.status,
                plan.triggered_on_str,
                plan.triggered_by,
                plan.started_on_str,
                plan.ended_on_str,
            )

        click.echo()
        console = Console()
        console.print(table)
        click.echo(f"Number of execution plans: {len(list_of_plans)}")
        click.echo()
    except Exception as e:
        raise click.ClickException(f"Failed to list execution plans: {e}")
