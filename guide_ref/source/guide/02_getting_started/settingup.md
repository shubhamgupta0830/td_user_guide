<!--
    Copyright 2024 Tabs Data Inc.
-->

<!-- ![TabsData](../media/getting_started/tabsdata.png) -->

**Copyright 2024 Tabs Data Inc.**

# Setting Up the Build and Run Environment

Before being able to build and run tabsdata from source code, you need to prepare your working environment with some initial requirements. The following guides for each of the relevant operating systems supported by tabsdata provide detailed steps to guide you in the process of preparation of this environment.

There might be alternate ways to get an equivalent environment. In these procedures, as it is customary and best practice, we prefer using a Python virtual environment. To prepare this environment, we relay on VirtualEnv, PyEnv, Miniconda & uv, but other virtualization tools should be also acceptable (although we do not test them).

## Pre-requisites

### Python

<<STEP: INCLUDE THE STEPS TO INSTALL PYTHON IN THE SYSTEM AS A PRE-REQUISITE>>

::::{tab-set}

:::{tab-item} MacOS

## MacOS Setup

## Assumptions

<div style="text-align: justify">
This guide is for MacOS with an ARM architecture. It is still valid for X86 architectures, but then you might need to adjust
some step or some download link.

The procedure below assumes your system is missing all the required solutions and components introduced in it. You should adapt
the steps described below if you already have installed or configured any of them. Some of the following steps can be carried 
out using diverse techniques and tools. We are relying on these that we consider that are more common, reliable or easy to use. 
You should also adapt the steps described below if you use other techniques or tools in your system.
</div>

## System Dependencies

<div style="text-align: justify">
<strong>Note</strong>: This procedure assumes your shell is <strong><i>zsh</i></strong>. At moments, you will be required to 
restart your shell to apply changes made in your shell environment. Please adjust these steps accordingly if using a different 
shell.
<br>
<br>
<strong>Note</strong>: We assume you system package manager is <strong><i>Homebrew</i></strong>. You might need to adjust the 
commands below if you are using a different system package manager.
</div>

## Homebrew Installation

If you don't already have it, install Homebrew using the command:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, you will be requested to run the following commands:

```
echo >> ~/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```
Although not mandatory, we recommend to restart your terminal now.

## Homebrew Update

Run the commands:

```
brew update
brew upgrade
```

## XCode Installation

If you don't already have it, install XCode from Apple Store. You can use this direct link to find it:

https://apps.apple.com/es/app/xcode/id497799835?l=en-GB&mt=12

## XCode Command Line Developer Tools

If you don't already have it, install XCode Command Line Developer Tools using the command:

```
xcode-select --install
```

## Docker Installation

You can use the following link to download the installer:

https://desktop.docker.com/mac/main/arm64/Docker.dmg

## Docker Start

Open the Docker app.

Docker is not normally necessary for regular development. But, you will need it if you have to run **all** the 
available unitary tests.

## Openssl Installation

Run the command:

```
brew install openssl
```

## Curl Installation

Run the command:

```
brew install curl
```
## Git Installation

Run the command:

```
brew install git
```

## Graphviz Installation

Run the command:

```
brew install graphviz
```

## Rust Installation

Run the command:

```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

The standard installation should be good enough in most cases. Use this option if you don't have any spcial needs.

After installation, restart your terminal. Then, if installation went fine, the following commands should succeed:

```
rustc --version
cargo --version
rustup doc
```

The minimum required Rust version to compile tabsdata is 1.81.0. Newer backward compatible versions might work and are 
supported. Currently, we use versions 1.83.0. Please check that the versions reported above are aligned 
with the supported versions.

## Cargo cargo-audit Installation

```
cargo install cargo-audit
```

## Cargo cargo-deny Installation

```
cargo install cargo-deny
```

## Cargo cargo-edit Installation

```
cargo install cargo-edit
```

## Cargo cargo-license Installation

```
cargo install cargo-license
```

## Cargo cargo-machete Installation

```
cargo install cargo-machete
```

## Cargo cargo-make Installation

```
cargo install cargo-make
```


## Cargo cargo-nextest Installation

```
cargo install cargo-nextest
```

## Cargo cargo-pants Installation

```
cargo install cargo-pants
```
## Installation of pyenv

```
brew install pyenv
```

After installation, restart your terminal. Then, if installation went fine, the following command should succeed:

```
pyenv --version
```

## Installation of miniconda

You can use the following link to download the installer:

https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg

After installation, restart your terminal.

Then, if installation went fine, the following command should succeed:

```
conda --version
```

If so, run then the command to update any updatable package:

```
conda update conda
```

You can run the following commands to make sure Miniconda is perfectly installed and configured:

```
conda create --name deleteme python=3.12
conda activate deleteme
python --version
pip --version
pyenv which python
pyenv which pip
which python
which pip
python3 --version
pip3 --version
conda deactivate
conda env remove --name deleteme
```

## Installation of uv

Run the command:

```
brew install uv
```

After installation, restart your terminal.

:::

:::{tab-item} Windows
Content 2
:::

:::{tab-item} Ubuntu
Content 2
:::

::::

**© Copyright 2024 Tabs Data Inc.**