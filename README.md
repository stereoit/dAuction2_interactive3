# dAuction2 application

Aplication to simulate double auction market. We are using Markdown for this
file.

## Windows prerequisites

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

### Install VirtualBox

VirtualBox is used for provisioning and running virtual machines. Install from the
[website](www.virtualbox.org)

### Install Vagrant

Vagrant is a technology to simplify bootstraping the workflow with virtual
environments.

We are using Fedora/RedHat virtual machines inside Vagrant, add them to the
vagrant stash:

    $ vagrant box add fedora-22-cloud https://download.fedoraproject.org/pub/fedora/linux/releases/22/Cloud/x86_64/Images/Fedora-Cloud-Base-Vagrant-22-20150521.x86_64.vagrant-libvirt.box


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

## Development Setup

This workflow can be used on from command-line/terminal. For PyCharm or other
IDE the workflow is bit different.

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


## Vagrant on Fedora using libvrit

If you are using Linux/Fedora for development, the VirtualBox provider is kinda
slow. One can utilize fast KVM/libvirt technology.

## Install vagrant libvirt plugin

    $ sudo dnf install libvirt-devel libxslt-devel libxml2-devel libvirt-devel libguestfs-tools-c
    $ vagrant plugin install vagrant-libvirt

## Add Fedora KVM box into Vagrant

    $ vagrant box add fedora-22-cloud https://download.fedoraproject.org/pub/fedora/linux/releases/22/Cloud/x86_64/Images/Fedora-Cloud-Base-Vagrant-22-20150521.x86_64.vagrant-virtualbox.box
    $ vagrant box list

## Use the libvirt provider when starting the box

    $ vagrant up --provider=libvirt

Rest is the same

