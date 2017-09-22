import os
from typing import Iterable, List, Optional

from bs4 import BeautifulSoup

import config
from webweeder import configutils
from webweeder import utils
from webweeder.domainconfig import DomainConfig
from webweeder.models import PageMetadata, page_metadata_from_json


class MonsterWeeder:
    # TODO: better logging, log each page as we process it or something
    # TODO: better error handling, one screwy HTML file shouldn't prevent weeding the rest

    def find_page_metadatas(self, directory: str) -> Iterable[str]:
        """
        :param directory: Where to look for metadata files
        :return: List of paths for the metadata files of each found page in the given directory, recursively
        """
        found_pages: List[str] = []
        for item_name in os.listdir(directory):
            item_path = os.path.join(directory, item_name)
            if os.path.isfile(item_path):
                if item_name == 'metadata.json':
                    found_pages.append(item_path)
            elif os.path.isdir(item_path):
                found_pages += self.find_page_metadatas(item_path)
            else:
                raise TypeError('Not a file or a directory: %s' % item_path)
        return found_pages

    def weed_page(self, base_dir: str, metadata_path: str):
        """
        :param base_dir: Top-level directory containing the raw HTML and plaintext files referred to by the metadata
        :param metadata_path: Full path to the metadata (i.e. already joined to base_dir)
        :return:
        """
        # Read and parse metadata
        meta: PageMetadata = page_metadata_from_json(utils.read_text_file(metadata_path, missing_ok=False))
        domain = configutils.get_config_for_domain(meta.domain)
        if domain is None:
            msg = 'No configuration found for domain "%s" while weeding page: %s' % (meta.domain, metadata_path)
            raise RuntimeError(msg)

        # Read raw HTML for the page
        raw_html_path = os.path.join(base_dir, meta.directory, meta.file_raw_html)
        raw_html = utils.read_text_file(raw_html_path, missing_ok=False)

        # Parse HTML and extract plaintext from article
        soup = BeautifulSoup(raw_html, config.HTML_PARSER)
        plaintext = self._extract_article_content(soup, domain)

        # Write plaintext to metadata_path
        plaintext_path = os.path.join(base_dir, meta.directory, meta.file_article_plaintext)
        utils.write_text_file(plaintext_path, plaintext, create_parents=True)

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
