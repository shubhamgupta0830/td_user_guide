#
# Copyright 2024 Tabs Data Inc.
#


from tabsdatasdk.datasetfunction import DatasetFunction, Input, Output
from tabsdatasdk.plugin import InputPlugin, OutputPlugin
from tabsdatasdk.uri import URI


def dataset(
    name: str,
    input: dict | Input | InputPlugin | None = None,
    output: dict | Output | OutputPlugin | None = None,
    trigger_by: str | URI | None = None,
) -> callable:
    """
    Decorator to set the input, output  and trigger_by parameters of a function and
        convert it to a DatasetFunction.

    Args:
        name (str): The name of the dataset.
        input (dict | Input | InputPlugin | None): Where to obtain the input of the
            function. It can be a dictionary, an Input, an InputPlugin or None.
        output (dict | Output | OutputPlugin | None): Where to store the output of
            the function. It can be a dictionary, an Output, an OutputPlugin or None.
        trigger_by (str | URI | None): The trigger to execute the function. It can be a
            dataset in the system or None (in which case it must be triggered manually).

    Returns:
        callable: The function converted to a DatasetFunction.
    """

    def decorator_tabset(func):
        return DatasetFunction(
            func, name, input=input, output=output, trigger_by=trigger_by
        )

    return decorator_tabset
