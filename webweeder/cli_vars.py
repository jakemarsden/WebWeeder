"""
Contains values which are too long and would otherwise just clutter up cli.py
"""

CHOICE_PARSERS = ['html.parser', 'html5lib', 'lxml']
CHOICE_LOGLEVEL = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

HELP_ALLDOMAINS = 'Set this flag to crawl every single configured domain, instead of specifying a list of them.'
HELP_CLEAN_CRAWL = 'Set this flag to remove anything in the output directory before crawling starts. ' \
                   'Using this flag without specifying any domains will clean the output directory and exit.'
HELP_CLEAN_WEED = 'Set this flag to remove all plaintext files in the output directory before crawling starts ' \
                  '(metadata and raw HTML files are preserved).'
HELP_OUTDIR = 'The directory to store results. Overrides any value set in "config.py".'
HELP_USERAGENT = 'The user agent string to use for crawling. Overrides any value set in "config.py".'
HELP_STATSINTERVAL = 'How often to log statistics, in seconds. Set to "-1" to disable statistics logging.'
HELP_PARSER = 'Which parser BeautifulSoup4 should use to parse HTML documents. ' \
              'See: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser for details.'
HELP_LOGLEVEL = 'Which messages to show on the console. Use DEBUG to show all messages. ' \
                'Note that all messages will be written to the log file regardless.'
HELP_LOGDIR = 'The directory to store log files. Overrides any value set in "config.py".'

MSG_CLEANING = 'Cleaning output directory'
MSG_CLEANING_AND_EXITING = '%s and exiting' % MSG_CLEANING

ERROR_ALLDOMAINS_WITH_LIST = 'You cannot specify a list of domains when the "--alldomains" flag is used. ' \
                             'See "webcrawl --help" for usage.'
ERROR_NO_DOMAIN_SPECIFIED = 'No domains specified. See "webcrawl --help" for usage.'
ERROR_UNCONFIGURED_DOMAIN = 'You are trying to crawl the "%s" domain, which hasn\'t been configured. ' \
                            'Make sure is has an entry in "config.py". See "webcrawl --help" for usage.'
ERROR_DUPLICATE_DOMAINS = 'You have specified the "%s" domain more than once, which is invalid. ' \
                          'See "webcrawl --help" for usage.'
ERROR_NOTHING_TO_WEED = 'There are no pages to weed. Have you tried the "webcrawl" command?'
