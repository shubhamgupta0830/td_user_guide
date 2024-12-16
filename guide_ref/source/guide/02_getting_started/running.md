<!--
    Copyright 2024 Tabs Data Inc.
-->

# Running Tabsdata

## Introduction

If you need to understand in depth the TabsData System, you can first read the [architecture](./architecture.md) document.
However, it is not needed to follow the procedure below.

To run an interact with a TabsData System, follow the steps described below. To be able to follow the guide below, you must go
through the steps in [compiling](./compiling.md). We will always assume you are in folder `<GIT_ROOT>` in your 
terminal, and that you built the system using profile `release`. If you specified no profile (`debug`), you can still 
follow the steps below just replacing any reference to `release` for `debug`.

## Tabsdata Python Setup

### Create the td Python environment

You will need a Python environment to run several components, both in the server and client sides. Therefore, a new (to avoid 
collision with the build tabsdata environment) Python interpreter is required before using them. We recommend having a dedicated 
virtual environment for these tasks. You can, again, ignore or adapt the steps related to setting up this virtual environment if 
you feel comfortable applying a different approach, as long as you can ensure an active Python environment with the necessary 
packages is available.

Note: you can choose any other name that you prefer more for this environment.

Run the commands:

```
conda deactivate
conda create --name td python=3.12
```

### Activate the td Python environment

Run the command:

```
conda activate td
```

### Install the Python Dependencies

Run the commands:

```
pip install uv
```

### Install the TabsData Python Packages

Run the commands:

```
cd ./client/td-sdk
pip install -I ".[test]"
cd ../..
```

### Install Utility Python Dependencies

The following dependencies are not necessary to run TabsDta. They are necessary here to run the example DataSet Function
you will run in this first tutorial.

Run the commands:

```
pip install -r ./client/td-sdk/examples/persons/requirements.txt
```

Please double-check you are back in folder `<GIT_ROOT>`.

## Server

The `tdserver` executable is the main component to manage TabsData instances from the server side. 

Run the command below to get the details of all available subcommands.

```
./target/release/tdserver --help
```

### Start the TabsData Server

Run the command:

```
./target/release/tdserver start
```

### Check the TabsData Server Status

Run the command:

```
./target/release/tdserver status
```

You should see that both `supervisor` and `apisrv` are running.

### Check the TabsData Server Logs

Run the command:

```
./target/release/tdserver log
```

You should see how log entries are being produced. Stop this with `CONTROL^C`.

Note: the **start** command above created a folder structure at **~/.tabsdata/instances/tabsdata**. The basename of this folder 
(**tabsdata**) is your current TabsData instance name. You can inspect the contents of this folder tree to understand how TabsData
Server information is organized.

## Client

The **td** executable is the main component to manage TabsData components from the client side. You can interact with a running server,
creating, modifying, removing and querying TabsData objects. 

Run the command below to get the details  of all available subcommands:

```
td --help
```

### Authentication

Use the subcommand below to log in to a running server:

```
td login <arguments>
```

Use the subcommand below to logout from a running server:

```
td logout <arguments>
```

Login information is stored locally so that you can reuse it from any terminal session.

### Server

Use the subcommand below to get the status of server you are loge in to:

```
td status <arguments>
```

### Users

Use the subcommand below to manage users on a running server:

```
td user <arguments>
```

### DataStores

Use the subcommand below to manage datastores on a running server:

```
td datastore <arguments>
```

### DataSets

Use the subcommand below to manage datasets on a running server:

```
td dataset <arguments>
```

### Execution Plans

Use the subcommand below to manage execution plans on a running server:

```
td execution-plan <arguments>
```

**© Copyright 2024 Tabs Data Inc.**