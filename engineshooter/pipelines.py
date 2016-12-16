# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class EngineshooterPipeline(object):
    def process_item(self, item, spider):
        return item


class MongodbPipeline(object):

    def __init__(self, settings):
        self.host, self.port = settings['MONGODB_HOST'], settings['MONGODB_PORT']
        self.mongo_db, self.mongo_coll = settings['MONGODB_DB'], settings['MONGODB_COLL']

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.host, self.port)
        db = self.client[self.mongo_db]
        self.collection = db[self.mongo_coll]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        spider.logger.info('Item add to MongoDB')
