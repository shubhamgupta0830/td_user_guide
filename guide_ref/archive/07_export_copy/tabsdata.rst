..
    Copyright 2024 Tabs Data Inc.

Tabsdata
=========


Single
--------

.. code-block:: python

    @td.dataset(
        input=td.TableInput("td://datastore/table"),
        output=td.TableOutput("output"),
    )


Multiple
---------

.. code-block:: python

    @td.dataset(
        input=td.LocalFileInput(
            path,
            format=format,
            initial_last_modified="2024-09-09T00:00:00",
        ),
        output=td.TableOutput(["output1", "output2"]),  # required,
    )