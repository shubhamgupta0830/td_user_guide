#
# Copyright 2024 Tabs Data Inc.
#

import os

import rich_click as click
from rich_click import Option, UsageError

DEFAULT_TABSDATA_DIRECTORY = os.path.join(os.path.expanduser("~"), ".tabsdata")


def beautify_list(list_to_show) -> str:
    if isinstance(list_to_show, list):
        return "\n".join(list_to_show)
    return str(list_to_show)


def logical_prompt(
    ctx: click.Context, message: str, default_value=None, hide_input: bool = False
):
    """
    Prompt the user for a value if prompt is enabled. Otherwise, either return the
        default value, or raise an error.
    """

    if ctx.obj["no_prompt"]:
        if default_value is None:
            raise click.ClickException(
                "Prompting is disabled and some required "
                "values are missing. Please provide the "
                "required values or avoid using '--no-prompt'."
            )
        return default_value
    return click.prompt(message, default=default_value, hide_input=hide_input)


class MutuallyExclusiveOption(Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        help = kwargs.get("help", "")
        if self.mutually_exclusive:
            ex_str = ", ".join(self.mutually_exclusive)
            kwargs["help"] = help + (
                " NOTE: This argument is mutually exclusive with  arguments: ["
                + ex_str
                + "]."
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise UsageError(
                "Illegal usage: `{}` is mutually exclusive with arguments `{}`.".format(
                    self.name, ", ".join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(ctx, opts, args)
