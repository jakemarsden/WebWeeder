import json
import os
import traceback
from datetime import datetime
from typing import Optional, Callable

from bs4 import BeautifulSoup
from pathvalidate import sanitize_file_path
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from config import OUTPUT_DIRECTORY
from tonyscraper.domainconfig import DomainConfig
from tonyscraper.models import PageMetadata
from tonyscraper.utils import DateTimeAwareJsonEncoder, write_text_file


class ClashdailyComSpider(CrawlSpider):
    # Horrible, horrible hack... I feel ashamed. Unsure how to pass in the domain any other way, although I'm sure it
    # must be possible.
    next_instance_domain: DomainConfig = None

    def __init__(self):
        domain = ClashdailyComSpider.next_instance_domain
        ClashdailyComSpider.next_instance_domain = None
        if domain is None:
            raise TypeError

        super().__init__(name=domain.name,
                         start_urls=domain.seed_urls,
                         allowed_domains=[domain.name],
                         rules=[
                             Rule(LinkExtractor(allow=['.*']), callback='parse_item', follow=True)
                         ])

        self.domain_config: DomainConfig = domain

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
