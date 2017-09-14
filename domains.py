from typing import List

from tonyscraper.domainconfig import DomainConfig, SimpleDomainConfig

DOMAIN_CONFIGS: List[DomainConfig] = [
    SimpleDomainConfig(name='altright.com',
                       url_patterns=['https://altright.com/*'],
                       seed_urls=['https://altright.com'],
                       article_title_selector='h3.post-title',
                       article_date_selector='div.date > a:first-child',
                       article_date_junk=['published on'],
                       article_content_selector='div.article-content'),
    SimpleDomainConfig(name='clashdaily.com',
                       url_patterns=['https://clashdaily.com/*'],
                       seed_urls=['https://clashdaily.com'],
                       article_title_selector='h1.wpdev-single-title',
                       article_date_selector='span.wpdev-article-date',
                       article_content_selector='div.wpdev-entry-content')
]
