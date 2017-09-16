# WebWeeder

A command-line tool for crawling and scraping information from websites for discourse analysis.

There are two main parts to the application:

- `tonycrawl` - Crawls a list of domains, downloads the raw HTML for each matching page and stores it alongside some metadata in JSON format
- `tonyscrape` - Extracts the required information from the raw HTML files and presents it in a usable format
- `config.py` - User-editable configuration file which contains configuration defaults and also defines how each domain should be crawled

This is a work in progress.

Both Windows and Linux are supported.
Python 2 is not supported.

## Usage

These instructions are for systems running Windows.
Adapt the instructions as needed to suit a Linux system.

### Install

1. Install the latest version of Python 3 from [here](https://python.org/downloads/) (enable the "Add Python 3.x to PATH" option when prompted)
1. Install the latest version of Git from [here](https://git-scm.com/downloads)
1. Create a folder named `WebWeeder` where you wish to install the application (just on your desktop is fine)
1. Open the folder and `Shift+RightClick`->`Open Command Window Here`
1. Enter these commands (press enter and wait for it to complete after each one):
    1. `python3 -m venv ./venv`
    1. `venv/bin/pip install -e git+https://github.com/jakemarsden/WebWeeder.git ./`
    1. Ensure it works: `tonycrawl --help`

### Update

1. Open the `WebWeeder` folder and `Shift+RightClick`->`Open Command Window Here`
1. Enter these commands (press enter and wait for it to complete after each one):
    1. `venv/bin/pip install -e git+https://github.com/jakemarsden/WebWeeder.git ./`
    1. Ensure it still works: `tonycrawl --help`

### Uninstall

1. Remove the `WebWeeder` folder you created during installation
1. Optionally uninstall Python 3
1. Optionally uninstall Git
