# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# class to process the found items

class CheckDouble(object):
    #this proces step drops any double item
    def process_item(self, item, spider):
        # proces the item
        print 'item hit the processor'
        return item

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item
