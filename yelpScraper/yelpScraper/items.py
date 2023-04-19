# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YelpscraperItem(scrapy.Item):
    City = scrapy.Field()
    Business_Name= scrapy.Field()
    Business_Primary_Category= scrapy.Field()
    Business_Address_Line1 = scrapy.Field()
    Business_Address_Line2 = scrapy.Field()
    Phone = scrapy.Field()
