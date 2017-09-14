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
        return any(re.compile(pattern).match(url) for pattern in self.url_patterns)

    def scrape_article_title(self, soup: BeautifulSoup) -> Optional[str]:
        raise NotImplementedError

    def scrape_article_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        raise NotImplementedError

    def scrape_article_content(self, soup: BeautifulSoup) -> Optional[str]:
        raise NotImplementedError

    def scrape_page_title(self, soup: BeautifulSoup) -> Optional[str]:
        raise NotImplementedError


class SimpleDomainConfig(DomainConfig):
    @classmethod
    def select_element(cls, soup: BeautifulSoup, selector: str) -> Optional[BeautifulSoup]:
        if selector is not None:
            return soup.select_one(selector)
        return None

    @classmethod
    def select_text(cls, soup: BeautifulSoup, selector: str) -> Optional[str]:
        element = cls.select_element(soup, selector)
        if element is not None:
            text = element.get_text()
            if text is not None:
                return text.strip()
        return None

    def parse_date(self, date_str: str) -> datetime:
        for junk in self.article_date_junk:
            date_str = re.sub(junk, '', date_str, flags=re.IGNORECASE)
            date_str = date_str.strip()
        return parse_date(date_str)

    def scrape_article_title(self, soup: BeautifulSoup) -> Optional[str]:
        return self.select_text(soup, self.article_title_selector)

    def scrape_article_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        date_str = self.select_text(soup, self.article_date_selector)
        if date_str is not None:
            return self.parse_date(date_str)
        return None

    def scrape_article_content(self, soup: BeautifulSoup) -> Optional[str]:
        return self.select_text(soup, self.article_content_selector)

    def scrape_page_title(self, soup: BeautifulSoup) -> Optional[str]:
        return self.select_text(soup, self.page_title_selector)
