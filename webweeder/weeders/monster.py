import os
from typing import Optional

from bs4 import BeautifulSoup

import config
from webweeder import configutils
from webweeder import utils
from webweeder.domainconfig import DomainConfig
from webweeder.models import PageMetadata, page_metadata_from_json


class MonsterWeeder:
    # TODO: better logging, log each page as we process it or something
    # TODO: better error handling, one screwy HTML file shouldn't prevent weeding the rest

    def weed(self):
        self._weed_subdirectory(config.OUTPUT_DIRECTORY)

    def _weed_file(self, file: str):
        # Read and parse JSON file
        json_str = utils.read_text_file(file, missing_ok=False)
        meta: PageMetadata = page_metadata_from_json(json_str)

        domain_config = configutils.get_config_for_domain(meta.domain)
        if domain_config is None:
            raise RuntimeError('Unconfigured domain "%s" for page: %r' % (meta.domain, meta))

        raw_html_path = os.path.join(config.OUTPUT_DIRECTORY, meta.directory, meta.file_raw_html)
        raw_html = utils.read_text_file(raw_html_path, missing_ok=False)

        soup = BeautifulSoup(raw_html, config.HTML_PARSER)
        plaintext = self._extract_article_content(soup, domain_config)

        plaintext_path = os.path.join(config.OUTPUT_DIRECTORY, meta.directory, meta.file_article_plaintext)
        utils.write_text_file(plaintext_path, plaintext)

    def _weed_subdirectory(self, dir: str):
        for item_name in os.listdir(dir):
            item_path = os.path.join(dir, item_name)
            if os.path.isfile(item_path):
                if item_name == 'metadata.json':
                    self._weed_file(item_path)
            elif os.path.isdir(item_path):
                self._weed_subdirectory(item_path)
            else:
                raise TypeError('Not a file or a directory: %s' % item_path)

    @staticmethod
    def _extract_article_content(soup: BeautifulSoup, domain: DomainConfig) -> Optional[str]:
        # TODO: Similar to DomainConfig.scrape_* methods, refactor needed?
        """
        IMPORTANT: This modifies the passed soup

        If configured selector is None, None is returned
        If configured selector is not None, the scraped article content is returned
        If configured selector is not None but the article content cannot be scraped, an error is raised
        """
        if domain.article_content_selector is None:
            return None
        for crap in soup.find_all(name='script'):
            crap.extract()
        for crap in soup.find_all(name='style'):
            crap.extract()
        element = soup.select_one(domain.article_content_selector)
        text = element.get_text()
        return text.strip()
