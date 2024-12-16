..
    Copyright 2024 Tabs Data Inc.

SQL/DB Import
==============

This section demonstrates how to read from a SQL database while defining a dataset in Tabsdata.

File path 
----------------

.. code-block:: python

    data = [
    "select * from INVOICE_HEADER where id > :number",
    "select * from INVOICE_ITEM where id > :number",
    ]

    @td.dataset(
        trigger="manual",
        input=td.MySQLInput(
            "mysql://path/to/db",
            data,
            credentials=td.UserPasswordCredentials("username", "passowrd"),
            initial_values={"number": 2},
        ),
        output={"tables": ("output1.json", "output2.json")},  # required,
    )

Modified Params
------------------

In case of the need to change specific parameters in the SQL based input, the following functions can be used:

.. code-block:: python
    
    mysql_input.uri = "mysql://localhost:3306/testing"
    mysql_input.query = data
    mysql_input.credentials = td.UserPasswordCredentials("username", "password")
    mysql_input.initial_values = {"number": 2}


Example:

.. code-block:: python

    data = [
        "select * from INVOICE_HEADER where id > :number",
        "select * from INVOICE_ITEM where id > :number",
    ]

    mysql_input = td.MySQLInput(
        "mysql://wrongip:3306/testing",
        ["select * from NO_TABLE where id > :number"],
        credentials=td.UserPasswordCredentials("wronguser", "wrongpassword"),
        initial_values={"number": 7},
    )

    mysql_input.uri = "mysql://localhost:3306/testing"
    mysql_input.query = data
    mysql_input.credentials = td.UserPasswordCredentials("username", "password")
    mysql_input.initial_values = {"number": 2}


    @td.dataset(
        trigger="manual",
        input=mysql_input,
        output={"tables": ("output1.json", "output2.json")},  # required,
    )