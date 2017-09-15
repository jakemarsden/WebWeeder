import os
from datetime import date
from typing import Dict, List

from tonyscraper.domainconfig import DomainConfig, SimpleDomainConfig
from tonyscraper.utils import date_range

_START_DATE = date(2013, 1, 1)
_END_DATE = date.today()
_DATES: List[date] = reversed(date_range(_START_DATE, _END_DATE))

# Can be overridden with command-line arguments, otherwise this is the default value
OUTPUT_DIRECTORY = os.path.join('out')

# Can be overridden with command-line arguments, otherwise this is the default value
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

# Can be overridden with command-line arguments, otherwise this is the default value
# Determines which parser BeautifulSoup4 will use to parse documents
HTML_PARSER = 'lxml'

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
                       url_patterns=[r'^https?://(www\.)?clashdaily.com/[0-9]{4}/[0-9]{2}/[^/]+/?$'],
                       # Seed with each daily summary page
                       seed_urls=['https://clashdaily.com/%04d/%02d/%0d2/' % (d.year, d.month, d.day) for d in _DATES],
                       article_title_selector='h1.wpdev-single-title',
                       article_date_selector='span.wpdev-article-date',
                       # Formats seen in the wild:
                       # - "Published on {Date}"
                       # - "Written by {Firstname} {Lastname} on {Date}"
                       article_date_junk=[r'^.*?on\s'],
                       article_content_selector='div.wpdev-entry-content')
]
