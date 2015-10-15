# dAuction2 application

Aplication to simulate double auction market. We are using Markdown for this
file.

## Development Setup

If you build on windows, please check bellow for detailed instructions.

### Checkout the code from github

    $ git clone https://github.com/ECON3/dAuction2_interactive3.git dAuction2

### Create and activate virtual environment

This is used to store all python related 3rd party libraries
(django,postgresql..). The folder is taken out from GIT revision using
.gitignore file. Initialize it as:

    $ cd dAuction2
    $ virtualenv venv

Activate the environment with:

    $ source venv/bin/activate

It can change the prompt of your shell. Activate the environment everytime you
are going to hack on the project.

### Install python requirements

With isolated project environmane one can install all python dependencies.

    (venv)~/C/w/dauction2 (code_cleanup) $ pip install -r requirements.txt


## Windows instalation

This section describes how to bootrap your windows development.

### Install ConEmu

ConEmu is powerfull windows terminal, replacing standard cmd command.

Download from [ConEmu website](https://conemu.github.io/)

### Install Python

At this moment it is recommended to use Python 2.7 branch (as some of the
libraries can use that as dependency). Obtain Windows installer from
[Python](www.python.org/downloads/release/python-2710/).

During installation select `Add python.exe to Path` last option, this will make
it easier to work with Python. Also make sure `PIP` is selected, this is a
package manager for python.

### Install GIT 

GIT is used for managing changes to the code. Obtain it from the [GIT
Website](https://git-scm.com/download/win).

During installation select "Use GIT and optional Unix tools from the Windows
Command Prompt" option.

### Optionally install PyCharm

PyCharm is very good IDE for development. It is recommended to use it for
development. Tested on the professional edition.

Once inside Pycharm:

1. Issue `Checkout from VCS system`
2. Login to GitHub
3. Use the [repository](https://github.com/ECON3/dAuction2_interactive3.git)
   for code checkout
4. Configure Python for the project
5. Start hacking.




