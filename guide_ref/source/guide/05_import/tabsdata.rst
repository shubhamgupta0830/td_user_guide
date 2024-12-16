..
    Copyright 2024 Tabs Data Inc.

Tabsdata Import
===================

This section demonstrates how to read from a Tabsdata database while defining a dataset in Tabsdata.

Single table input
-------------------

.. code-block:: python

    @td.dataset(
        input=td.TableInput("td://datastore/table"),
        output={"tables": ("output.json",)},
    )

Multiple tables input
-----------------------

.. code-block:: python

    @td.dataset(
        input=td.TableInput(
            ["td://datastore/invoice_headers", "td://datastore/invoice_items@HEAD^..HEAD"]
        ),
        output={"tables": ("output1.json", "output2.json")},
    )

