import os
from datetime import date
from typing import List, Tuple

from tonyscraper.domainconfig import DomainConfig, SimpleDomainConfig


def _range_yr_mth(start_yr: int, end_yr: int = date.today().year) -> List[Tuple[int, int]]:
    """
    :param start_yr:
    :param end_yr:
    :return: A list of tuples containing all month/year combinations in the given range of years (inclusive)
    """
    return [(yr, mth) for yr in range(start_yr, end_yr + 1) for mth in range(1, 13)]


# Can be overridden with command-line arguments, otherwise this is the default value
OUTPUT_DIRECTORY = os.path.join('out')

# Can be overridden with command-line arguments, otherwise this is the default value
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

DOMAINS: List[DomainConfig] = [
    SimpleDomainConfig(name='altright.com',
                       url_patterns=['https://altright.com/*'],
                       seed_urls=['https://altright.com'],
                       article_title_selector='h3.post-title',
                       article_date_selector='div.date > a:first-child',
                       article_content_selector='div.article-content'),
    SimpleDomainConfig(name='clashdaily.com',
                       url_patterns=[r'^https?://(www\.)?clashdaily.com/[0-9]{4}/[0-9]{2}/[^/]+/?$'],
                       # Seed with every single monthly summary page since 2013
                       seed_urls=[('https://clashdaily.com/%04d/%02d/' % yr_mth)
                                  for yr_mth in reversed(_range_yr_mth(2013))],
                       article_title_selector='h1.wpdev-single-title',
                       article_date_selector='span.wpdev-article-date',
                       # Formats seen in the wild:
                       # - "Published on {Date}"
                       # - "Written by {Firstname} {Lastname} on {Date}"
                       article_date_junk=[r'^.*?on\s'],
                       article_content_selector='div.wpdev-entry-content')
]
