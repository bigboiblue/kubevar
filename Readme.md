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
Run the following command in a terminal with a POSIX compliant shell:

    git clone https://gitlab.com/bit-memo/devtools/varsub.git
    chmod +x varsub/varsub
    sudo mv varsub/varsub /usr/local/bin/varsub
    echo y | rm -R ./varsub

Since this is a private repo, your gitlab credentials are required

---
To uninstall, simply use:

    sudo rm /usr/local/bin/varsub

### Windows
This is not currently supported for windows (except through virtualising Linux, perhaps through cygwin etc)
