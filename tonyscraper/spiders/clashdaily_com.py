import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_file_path
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from tonyscraper.items import PageItem
from tonyscraper.utils import write_text_file


class ClashdailyComSpider(CrawlSpider):
    name = 'clashdaily.com'
    allowed_domains = ['clashdaily.com']
    start_urls = ['http://clashdaily.com/']

    rules = [
        Rule(LinkExtractor(allow=['.*']), callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        url = response.url
        title = response.css('title::text').extract_first()
        html = response.text

        item = PageItem()
        item['url'] = url
        item['title'] = title
        item['html'] = html
        item['plaintext'] = _html_to_plaintext(html)

        _persist(item)

        return item


def _html_to_plaintext(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for crap in soup(['script', 'style']):
        crap.extract()

    text = soup.body.get_text(separator=' ')
    return text


def _persist(item: PageItem):
    # file_name = hash_str(item['url'])
    file_name: str = item['url']
    while file_name.endswith('/') or file_name.endswith('\\'):
        file_name = file_name[:-1]
    file_name = sanitize_file_path(file_name, replacement_text='_')

    html_file = os.path.join('./cache', '%s.html' % file_name)
    plaintext_file = os.path.join('./cache', '%s.txt' % file_name)

    write_text_file(html_file, item['html'])
    write_text_file(plaintext_file, item['plaintext'])
