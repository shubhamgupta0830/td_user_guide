# Compiling the Project

### Creation of tabsdata Python environment

Some of the build tools employed in tabsdata rely on Python. Therefore, a Python interpreter is required before using them. We recommend 
having a dedicated virtual environment for these tasks. You can ignore or adapt the steps related to setting up this virtual environment
if you feel comfortable applying a different approach, as long as you can ensure an active Python environment with the necessary packages
is available.

Note: you can choose any other name that you prefer more for this environment.

Run the command:

```
conda create --name tabsdata python=3.12
```

### Activation of tabsdata Python environment

Run the command:

```
conda activate tabsdata
```

### Update of pip in the tabsdata Python environment

Run the command:

```
python3 -m pip install --upgrade pip
```

### Project root container

Choose or create freely the folder that will hold the tabsdata project. It is strongly recommended to avoid white spaces
in the folder name and path.

From now, we will refer to this folder as`< TD_ROOT>`.

### Project tabsdata Download

Run the command:

```
cd <TD_ROOT>
git clone git@github.com:tabsdata/tabsdata.git
```

Inside `<TD_ROOT>` you will have now a subfolder named `tabsdata`. From now, we will refer to this folder as `<GIT_ROOT>`.  

### Python Dependencies Installation

Run the commands:

```
cd tabsdata
cd client/td-sdk
pip  install ".[test]"
cd ../..
```

### Clean tabsdata Project

Run the command:

```
cargo make clean
```

Or, equivalently:

```
makers clean
```

### Compile tabsdata Project

Run the command:

```
cargo make build
```

Or, equivalently:

```
makers build
```

These steps will generate a debug build. If you need instead a release build, run command:

```
cargo make --env profile=release build
```

## Validating the Project (Optional)

There are several tasks that you can run the check the correctness of the code.

- **Unitary Tests**

Run commands:

```
MARKERS="not integration" cargo make test
```

Some tests require some additional setup, but explaining this falls out of the scope of this introduction.

### Rust Unitary Tests Only

To run only the Rust tests, use command

```
cargo make test_rs
```

### Python Unitary Tests Only

To run only the Python tests, use command

```
MARKERS="not integration" cargo make test_py
```

**Note**: as you can notice, most tasks in cargo make, that you can inspect running command 

```
cargo make --list-all-steps
```

support being suffixed with `_rs*`or `_py` to run them only for the Rust subprojects or the
Python subprojects.

- **Errors Checks**

Run command:

```
cargo make check
```

- **Format Checks**

Run command:

```
cargo make fmt
```

- **Licenses Checks**

Run command:

```
cargo make license
```

- **Upgrades Checks**

Run command:

```
cargo make upgrade
```

- **Dependencies Checks**

Run command:

```
cargo make deny
```

- **Vulnerabilities Checks**

Run command:

```
cargo make audit
```

- **Security Checks**

Run command:

```
cargo make pants
```

- **Security Checks**

Run command:

```
cargo make pants
```

- **Remnants Checks**

Run command:

```
cargo make pants
```

- **Mistakes Checks**

Run command:

```
cargo make clippy
```

## Project's Documentation (Optional)

You can generate the project's documentation with the following command:


```
cargo make doc
```

If you have chrome in your system, you can open the documentation with the following tasks:

- **Rust Code**

```
cargo make chrome_rs
```

- **Python Code**

```
cargo make chrome_py
```

If Chrome is unavailable, you can stilt open easily the documentation with these tasks:

- **Rust Code**

```
cargo make open_doc_rs
```

- **Python Code**

```
cargo make open_doc_py
```

To open the Python SDK API documentation, run the commands:

```
export PYTHONPATH=$PYTHONPATH:$(pwd)/client/td-sdk/tabsdatasdk
cd client/td-sdk
pdoc -- tabsdatasdk
cd ../..
```

## Building the Project (Optional)

To run the whole set of tasks from compilation to generation, you can run the command: 

```
cargo make
```

**© Copyright 2024 Tabs Data Inc.**