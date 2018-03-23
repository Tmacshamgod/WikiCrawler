# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WikicrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    path_root = scrapy.Field()
    depth = scrapy.Field()
    status = scrapy.Field()
