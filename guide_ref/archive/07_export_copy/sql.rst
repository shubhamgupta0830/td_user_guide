..
    Copyright 2024 Tabs Data Inc.

SQL
====


Multiple
----------

.. code-block:: python

    @td.dataset(
        input=td.LocalFileInput(os.path.join(ABSOLUTE_LOCATION, "data.csv")),
        output=td.MySQLOutput(
            "mysql://localhost:3306/testing",
            ["output_sql_list", "second_output_sql_list"],
            credentials=td.UserPasswordCredentials("@dmIn", "p@ssw0rd#"),
        ),
    )


Modified Params
--------------------

.. code-block:: python

    sql_output = td.MySQLOutput(
        "mysql://wrongip:3306/testing",
        ["wrong_table", "second_second_wrong_table"],
        credentials=td.UserPasswordCredentials("wronguser", "wrongpassword"),
    )

    sql_output.uri = "mysql://localhost:3306/testing"
    sql_output.destination_table = [
        "output_sql_modified_params",
        "second_output_sql_modified_params",
    ]
    sql_output.credentials = td.UserPasswordCredentials("@dmIn", "p@ssw0rd#")


    @td.dataset(
        input=td.LocalFileInput(os.path.join(ABSOLUTE_LOCATION, "data.csv")),
        output=sql_output,
    )