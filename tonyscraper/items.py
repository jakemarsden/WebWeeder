# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PageItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    html = scrapy.Field()
    plaintext = scrapy.Field()
