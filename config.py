import os
from datetime import date
from typing import Dict, List

from webweeder.domainconfig import DomainConfig, SimpleDomainConfig
from webweeder.utils import date_range

_START_DATE = date(2013, 1, 1)
_END_DATE = date.today()
_DATES: List[date] = [d for d in reversed(date_range(_START_DATE, _END_DATE))]

# Can be overridden with command-line arguments, otherwise this is the default value
OUTPUT_DIRECTORY = os.path.join('out')

# Can be overridden with command-line arguments, otherwise this is the default value
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

# Can be overridden with command-line arguments, otherwise this is the default value
# How often to log statistics (in seconds), or -1 to disable
STATS_INTERVAL = 10

# Can be overridden with command-line arguments, otherwise this is the default value
# Determines which parser BeautifulSoup4 will use to parse documents
HTML_PARSER = 'lxml'

# Can be overridden with command-line arguments, otherwise this is the default value
LOG_LEVEL = 'INFO'

# Can be overridden with command-line arguments, otherwise this is the default value
# Determines where log files are stored
LOG_DIRECTORY = os.path.join('logs')

# The settings given to Scrapy for crawling. Must be set by CLI on program start
SCRAPY_SETTINGS: Dict[str, object] = None

DOMAINS: List[DomainConfig] = [
    SimpleDomainConfig(name='altright.com',
                       url_patterns=[r'^https?://(www\.)?altright.com/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/]+/?$'],
                       # Seed with each daily summary page
                       seed_urls=['https://altright.com/%04d/%02d/%02d/' % (d.year, d.month, d.day) for d in _DATES],
                       article_title_selector='h3.post-title',
                       article_date_selector='.post-meta div.date > a',
                       article_content_selector='div.article-content'),
    SimpleDomainConfig(name='clashdaily.com',
                       # If you're here because this RegEx is broken, the best thing to do is delete all traces of the
                       # application, cut ties with everyone you know and begin a new life somewhere far, far away.
                       #
                       # "^" matches the start of the string
                       # "https?" matches both "http" and "https"
                       # "(www\.)?" matches both "" and "www."
                       # "[0-9]{4}" matches 4 consecutive digits
                       # "[^/]+" matches one or more characters which aren't "/"
                       # "(?<!/[0-9]{2})/?" matches (both "" and "/"), unless it is preceded by "/[0-9]{2}"
                       # "$" matches the end of the string
                       #
                       url_patterns=[r'^https?://(www\.)?clashdaily.com/[0-9]{4}/[0-9]{2}/[^/]+(?<!/[0-9]{2})/?$'],
                       # Seed with each daily summary page
                       seed_urls=['https://clashdaily.com/%04d/%02d/%02d/' % (d.year, d.month, d.day) for d in _DATES],
                       article_title_selector='h1.wpdev-single-title',
                       article_date_selector='span.wpdev-article-date',
                       # Formats seen in the wild:
                       # - "Published on {Date}"
                       # - "Written by {Firstname} {Lastname} on {Date}"
                       article_date_junk=[r'^.*?on\s'],
                       article_content_selector='div.wpdev-entry-content')
]
