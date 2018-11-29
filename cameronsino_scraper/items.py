# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CameronsinoScraperItem(scrapy.Item):
    url = scrapy.Field()
    base_image = scrapy.Field()
    small_image = scrapy.Field()
    thumbnail_image = scrapy.Field()
    additional_images = scrapy.Field()
    CategoryImage = scrapy.Field()
    Categories = scrapy.Field()
    SubCategories = scrapy.Field()
    SKU = scrapy.Field()
    Brand = scrapy.Field()
    Bar_Code = scrapy.Field()
    Volts = scrapy.Field()
    Type = scrapy.Field()
    Capacity = scrapy.Field()
    Color = scrapy.Field()
    Dimension = scrapy.Field()
    Price = scrapy.Field()
    NetWeightGrams = scrapy.Field()
    NetWeightPounds = scrapy.Field()
    GrossWeightGrams = scrapy.Field()
    GrossWeightPounds = scrapy.Field()
    Part_No = scrapy.Field()
    Fit_Model = scrapy.Field()
    Stock = scrapy.Field()
    Condition = scrapy.Field()
    Remark = scrapy.Field()
    MOQ = scrapy.Field()
