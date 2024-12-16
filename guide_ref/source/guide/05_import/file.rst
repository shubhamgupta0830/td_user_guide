..
    Copyright 2024 Tabs Data Inc.

File import
============

This section demonstrates different ways to read files in Tabsdata. For each kind there is an option to import the file from either local system or Aws S3. Both ways have been highlighted below.


Format based
---------------

In this method, the format of file is defined separately from the path to file. Three kinds of formats are supported currently: 

* ``csv``
* ``log``
* ``parquet``

You can replace ``format="csv"`` below with ``format="log"`` or ``format="parquet"`` as needed.

Local File Input
^^^^^^^^^^^^^^^^^^
.. code-block:: python

    @td.dataset(
        input=td.LocalFileInput(("path/to/file/data"), format="csv"),
        output=td.TableOutput("output"),
    )


Aws S3 
^^^^^^^^^^^^^
.. code-block:: python

    s3_credentials = td.S3AccessKeyCredentials (
    os.environ.get("AWS_ACCESS_KEY_ID", "FAKE_ID"),
    os.environ.get("AWS_SECRET_ACCESS_KEY", "FAKE_KEY"),
    )

    @td.dataset(
        input=td.S3Input(
        "s3://path/to/file/data", s3_credentials, format="csv"
    ),
        output=td.TableOutput("output"),
    )


File path
----------------

In the method, the file name is directly mentioned. In the below examples the file type is ``.csv``. It can be ``.log`` or ``.parquet`` file as well. 

Local File Input
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @td.dataset(
        input=td.LocalFileInput("path/to/file/data.csv"),
        output=td.TableOutput("output"),
    )

Aws S3 
^^^^^^^^^^^^^
.. code-block:: python

    s3_credentials = td.S3AccessKeyCredentials (
    os.environ.get("AWS_ACCESS_KEY_ID", "FAKE_ID"),
    os.environ.get("AWS_SECRET_ACCESS_KEY", "FAKE_KEY"),
    )

    @td.dataset(
        input=td.S3Input(
        "s3://path/to/file/data.csv", s3_credentials
    ),
        output=td.TableOutput("output"),
    )


Wildcard import
-----------------

This is to import mutiple files with similar names at once. As in above example, ``.log`` and ``.parquet`` formats are supported as well.

Local File Input
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @td.dataset(
        input=td.LocalFileInput("path/to/file/source_*.csv"),
        output=td.TableOutput("output"),
    )

Aws S3 
^^^^^^^^^^^^^
.. code-block:: python

    s3_credentials = td.S3AccessKeyCredentials (
    os.environ.get("AWS_ACCESS_KEY_ID", "FAKE_ID"),
    os.environ.get("AWS_SECRET_ACCESS_KEY", "FAKE_KEY"),
    )

    @td.dataset(
        input=td.S3Input(
        "s3://path/to/file/source_*.csv", s3_credentials
    ),
        output=td.TableOutput("output"),
    )


Multiple files
----------------

Multiple files can be imported at once, as highlighted below.

Local File Input
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    path = [
        "path/to/file/invoice-headers.csv",
        "path/to/file/invoice-items-*.csv",
    ]

    @td.dataset(
        input=td.LocalFileInput(
            path,
        ),
        output=td.TableOutput("output"),
    )

Aws S3 
^^^^^^^^^^^^^

.. code-block:: python

    path = [
        "s3://path/to/file/invoice-headers.csv",
        "s3://path/to/file/invoice-items-*.csv",
    ]

    s3_credentials = td.S3AccessKeyCredentials (
    os.environ.get("AWS_ACCESS_KEY_ID", "FAKE_ID"),
    os.environ.get("AWS_SECRET_ACCESS_KEY", "FAKE_KEY"),
    )


    @td.dataset(
        input=td.S3Input(
            path, s3_credentials
        ),
        output=td.TableOutput("output"),
    )


Separator based *(Only for CSV)*
--------------------------------

Tabsdata supports single-byte characters as a separator for CSV files. A single character, such as a comma ``(,)``, semicolon ``(;)``, tab ``(\t)``, or space ``( )``, can be specified as the delimiter when reading a CSV file.


Local File Input
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @td.dataset(
        input=td.LocalFileInput("path/to/file/data.csv", format=td.CSVFormat(separator=";")
        ),
        output=td.TableOutput("output"),
    )

Aws S3 
^^^^^^^^^^^^^
.. code-block:: python

    s3_credentials = td.S3AccessKeyCredentials (
    os.environ.get("AWS_ACCESS_KEY_ID", "FAKE_ID"),
    os.environ.get("AWS_SECRET_ACCESS_KEY", "FAKE_KEY"),
    )

    @td.dataset(
        input=td.S3Input(
        "s3://path/to/file/data.csv", s3_credentials, format=td.CSVFormat(separator=";")
    ),
        output=td.TableOutput("output"),
    )