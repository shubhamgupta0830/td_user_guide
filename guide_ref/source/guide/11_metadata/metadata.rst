..
    Copyright 2024 Tabs Data Inc.

Metadata
=============

Managing and cataloging metadata
---------------------------------------------

Given a dataset, the following metadata is available:

* all the :ref:`tabfunctions <tabfunction>` uploaded, the last one is the active one. For each tabfunction you can see dependencies, :ref:`trigger<trigger>` and :ref:`tables<table>` it produces.
* all the :ref:`dataset versions<dataset_version>`, timestamp of when the version was published and which tabfunction was used to create the dataset version.
* as part of which trigger execution the dataset version was generated. <<Doubt: How will it be differentiated from the tabfunction mentioned in the point above?>>
* given dataset version and a table, the schema of the table is available.

Syncing metadata with external systems
---------------------------------------------