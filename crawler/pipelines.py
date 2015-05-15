# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# class to process the found items
import sqlite3 as lite
from scrapy.utils.project import get_project_settings
import datetime, time

class CheckDouble(object):
    #this proces step drops any double item
    def process_item(self, item, spider):
       # proces the item
        settings = get_project_settings()
        db = lite.connect(settings.get("DB"))
        db.row_factory = lite.Row
        
        cur = db.execute("select * from result where description = ?", (str(item["description"]),))
        row = cur.fetchone()

        if row is None:
            print 'New item found, adding to DB'
        else:
            db.close()
            return item
        
        db.execute("insert into result(objective, score, url, base_url, price, description, date_posted, date_found) values (?, ?, ?, ?, ?, ?, ?, ?)", (int(item["objective_id"]), int(0), str(item["url"]), item["url_id"], item["price"], str(item["description"]), item["date_posted"], datetime.datetime.utcfromtimestamp(time.time()))) 
        
        db.commit()
        db.close()
        return item

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item
