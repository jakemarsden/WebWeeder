"""
Contains values which are too long and would otherwise just clutter up cli.py
"""

CHOICE_LOGLEVEL = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

HELP_OUTDIR = 'The directory to store results. Overrides any value set in "config.py".'
HELP_USERAGENT = 'The user agent string to use for crawling. Overrides any value set in "config.py".'
HELP_LOGLEVEL = 'Which messages to show on the console. Use DEBUG to show all messages.'

ERROR_NO_DOMAIN_SPECIFIED = 'No domains specified. See "tonycrawl --help" for usage.'
ERROR_UNCONFIGURED_DOMAIN = 'You are trying to crawl the "%s" domain, which hasn\'t been configured. ' \
                            'Make sure is has an entry in "config.py". See "tonycrawl --help" for usage.'
ERROR_DUPLICATE_DOMAINS = 'You have specified the "%s" domain more than once, which is invalid. ' \
                          'See "tonycrawl --help" for usage.'
