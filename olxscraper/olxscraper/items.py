# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from pprint import pformat


def short_url(url):
    if len(url) <= 50:
        return url
    return url[:25] + '...' + url[-25:]


class VehicleItem(scrapy.Item):
    url_hash = scrapy.Field()
    html_hash = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    html = scrapy.Field()
    visited_on = scrapy.Field()

    def __repr__(self):
        return pformat({
            'url_hash': self['url_hash'],
            'html_hash': self['html_hash'],
            'category': self['category'],
            'url': short_url(self['url']),
            'visited_on': str(self['visited_on'])
        })
