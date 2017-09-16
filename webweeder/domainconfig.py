import re
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date


class DomainConfig:
    def __init__(self,
                 name: str,
                 url_patterns: List[str],
                 seed_urls: List[str],
                 page_title_selector: Optional[str] = 'title',
                 article_title_selector: Optional[str] = None,
                 article_date_selector: Optional[str] = None,
                 article_date_junk: Optional[List[str]] = None,
                 article_content_selector: Optional[str] = None):
        """
        :param name:
        :param url_patterns:
        :param seed_urls:
        :param page_title_selector:
        :param article_title_selector:
        :param article_date_selector:
        :param article_date_junk: Ordered list of regular expressions to remove from article dates, eg. clashdaily.com
        article dates are prefixed with: "Published on"
        :param article_content_selector:
        """
        if article_date_junk is None:
            article_date_junk = []
        self.name: str = name
        self.url_patterns: List[str] = url_patterns
        self.seed_urls: List[str] = seed_urls
        self.page_title_selector: Optional[str] = page_title_selector
        self.article_title_selector: Optional[str] = article_title_selector
        self.article_date_selector: Optional[str] = article_date_selector
        self.article_date_junk: List[str] = article_date_junk
        self.article_content_selector: Optional[str] = article_content_selector

    def includes_url(self, url: str) -> bool:
        for pattern in self.url_patterns:
            regex = re.compile(pattern)
            if regex.match(url) is not None:
                return True
        return False

    def scrape_article_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        If 'article_title_selector' is None, None is returned
        If 'article_title_selector' is not None, the scraped article title is returned
        If 'article_title_selector' is not None but the article title cannot be scraped, an error is raised
        """
        raise NotImplementedError

    def scrape_article_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """
        If 'article_date_selector' is None, None is returned
        If 'article_date_selector' is not None, the scraped article date is returned
        If 'article_date_selector' is not None but the article date cannot be scraped, an error is raised
        """
        raise NotImplementedError

    def scrape_page_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        If 'page_title_selector' is None, None is returned
        If 'page_title_selector' is not None, the scraped page title is returned
        If 'page_title_selector' is not None but the page title cannot be scraped, an error is raised
        """
        raise NotImplementedError


class SimpleDomainConfig(DomainConfig):
    @classmethod
    def select_text(cls, soup: BeautifulSoup, selector: Optional[str]) -> Optional[str]:
        """
        If the given selector is None, None is returned
        If the given selector is not None, text from the matching element is returned
        If the given selector is not None but it doesn't match anything, an error is raised
        """
        if selector is None:
            return None
        element = soup.select_one(selector)
        text = element.get_text()
        return text.strip()

    def parse_date(self, date_str: str) -> datetime:
        """
        Raises if the given date string cannot be parsed
        """
        for junk in self.article_date_junk:
            date_str = re.sub(junk, '', date_str, flags=re.IGNORECASE)
            date_str = date_str.strip()
        return parse_date(date_str)

    def scrape_article_title(self, soup: BeautifulSoup) -> Optional[str]:
        return self.select_text(soup, self.article_title_selector)

    def scrape_article_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        date_str = self.select_text(soup, self.article_date_selector)
        return self.parse_date(date_str) if (date_str is not None) else None

    def scrape_page_title(self, soup: BeautifulSoup) -> Optional[str]:
        return self.select_text(soup, self.page_title_selector)
