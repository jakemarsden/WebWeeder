# WebWeeder

A command-line tool for crawling and scraping information from websites for discourse analysis.

There are two main parts to the application:

- `webcrawl` - Crawls a list of domains, downloads the raw HTML for each matching page and stores it alongside some metadata in JSON format
- `webweed` - Extracts the required information from the raw HTML files and presents it in a usable format
- `config.py` - User-editable configuration file which contains configuration defaults and also defines how each domain should be crawled

This is a work in progress.

Both Windows and Linux are supported.
Python 2 is not supported.
