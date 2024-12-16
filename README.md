Copyright 2024 Tabs Data Inc.

# README for User Guide

## About

This folder contains the work-in-progress version of the user guide. The documentation is being created using reStructuredText (RST) with Sphinx.

## Folder Structure

The `guide` folder contains the `source` directory that contains the base RST files and is the primary workspace for documentation development.

#### Required Files and Folders

The following files and folders are essential for the system to function properly:

1. `index.rst`
2. `conf.py`
3. `_static` (folder)
4. `_templates` (folder)

All other files and folders in the `source` directory relate to the specific documentation content and can be modified as needed.

## Local Build Instructions

To view the output in HTML for any changes made in local, follow these steps:

### Step 1. Install Sphinx

Choose one of the following methods to install Sphinx:

- Using pip:
  ```bash
  pip install -U sphinx
- Or, using conda:
  ```bash
  conda install sphinx
- Or, for MacOS users with Homebrew:
  ```bash
  conda install sphinx
- Or, for Windows users with Chocolatey:
  ```bash
  choco install sphinx
For more installation details, visit the [Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/installation.html#pypi-package).

### Step 2. Install Sphinx ReadTheDocs theme

- Using pip:
  ```bash
  pip install sphinx_rtd_theme
### Step 3: Build the Documentation

1. Open a terminal and navigate to the `guide` directory.
2. Clean out any existing builds with the following command:

    ```bash
    make clean
    ```

3. Run the Sphinx build command to generate HTML:

    ```bash
    sphinx-build -M html source build
    ```

4. Open the `index.html` file in the `build/html` folder to view the generated documentation.

5. To apply any subsequent changes, build the html again using `sphinx-build -M html source build`. (Note: For any changes in base files such as index.rst or conf.py, you will need to clean the build files first using `make clean` and then build the files using `sphinx-build -M html source build`.)
