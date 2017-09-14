import json
import os
import traceback
from datetime import datetime
from typing import Optional, Callable

from bs4 import BeautifulSoup
from pathvalidate import sanitize_file_path
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from config import DOMAINS, OUTPUT_DIRECTORY
from tonyscraper.domainconfig import DomainConfig
from tonyscraper.models import PageMetadata
from tonyscraper.utils import DateTimeAwareJsonEncoder, write_text_file


class ClashdailyComSpider(CrawlSpider):
    name = 'clashdaily.com'

    rules = [
        # Allow all pages through as we're already restricting to the correct domain
        Rule(LinkExtractor(allow=['.*']), callback='parse_item', follow=True)
    ]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.domain_config: DomainConfig = DOMAINS[1]  # TODO: pass the correct domain config from somewhere else
        self.start_urls = self.domain_config.seed_urls
        self.allowed_domains = [self.domain_config.name]

    @classmethod
    def get_output_directory(cls, url: str) -> str:
        while '//' in url:
            url = url.replace('//', '/')
        if url.endswith('/'):
            url = url[:-1]
        return sanitize_file_path(url, replacement_text='_')

    def parse_item(self, response):
        now = datetime.utcnow()
        url = response.url
        domain = self.domain_config

        if not domain.includes_url(url):
            self.logger.info('Skipping over URL: %s' % url)
            return {'url': url, 'matches': False}

        self.logger.info('Crawler found: %s' % url)

        soup = BeautifulSoup(response.text)

        meta = PageMetadata()
        meta.domain = domain.name
        meta.url = url
        meta.url_date = now
        meta.page_title = self._try_get(url, 'page title', lambda: domain.scrape_page_title(soup))
        meta.article_title = self._try_get(url, 'article title', lambda: domain.scrape_article_title(soup))
        meta.article_date = self._try_get(url, 'article date', lambda: domain.scrape_article_date(soup))
        meta.directory = self.get_output_directory(url)
        meta.file_metadata = 'metadata.json'
        meta.file_raw_html = 'raw.html'
        meta.file_article_plaintext = 'plaintext_article.txt'

        meta_json = json.dumps(meta, indent=4, sort_keys=False, cls=DateTimeAwareJsonEncoder)
        raw_html = response.text

        write_text_file(os.path.join(OUTPUT_DIRECTORY, meta.directory, meta.file_metadata), meta_json)
        write_text_file(os.path.join(OUTPUT_DIRECTORY, meta.directory, meta.file_raw_html), raw_html)

        return {'url': url, 'matches': True}

    def _try_get(self, url: str, msg: str, func: Callable[[], object]) -> Optional[object]:
        result = None
        try:
            result = func()
        except Exception:
            self.logger.warning('Unable to parse %s: %s' % (msg, url))
            self.logger.debug(traceback.format_exc())
        else:
            if result is None:
                self.logger.warning('Unable to parse %s: %s' % (msg, url))
        return result
