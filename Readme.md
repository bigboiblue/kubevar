## Dependencies



# 

## Introduction

- Bringing variable substitution to kubernetes! Both static and dynamic... Scrap Kustomize!)

## Dependencies

### Runtime

- Python3 ([install here](https://www.python.org/downloads/))

### Static

- All static / internal dependencies are included in the requirements.txt file. These are installed automatically through running the installer.


## Installation

### Mac and Linux

#### Development

In order to setup the virtual environment (venv) for development, run the following commands:

    git clone https://gitlab.com/kubevar/kubevar-tk.git
    cd kubevar-tk
    chmod +x setup_venv.sh
    ./setup_venv.sh

Since this is a private repo, your gitlab credentials are required

### Windows

#### Development

A setup tool has not yet been created for windows, though the steps are quite simple. Open and analyse setup_venv.sh, then mimic the commands used using the MS_DOS equivalent

