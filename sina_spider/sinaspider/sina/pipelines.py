# -*- coding: utf-8 -*-

from sina.util import sqlUtil
from sina.items import *


class SinaPipeline(object):
    def open_spider(self, spider):
        self.db = sqlUtil.DBUtil()

    def process_item(self, item, spider):

        if isinstance(item, SinaItem):
            print(item, 'Attention')
            sql = 'INSERT INTO attention(blogger, attentionLink, name, fansTotal, headshot) VALUES (%s,%s,%s,%s,%s)'
            params = (item['blogger'], item['attentionLink'], item['name'], item['fansTotal'], item['headshot'])
            self.db.otherOprate(sql, params=params)

        elif isinstance(item, SinaFansItem):
            print(item, 'Fans')
            sql = 'INSERT INTO fans(blogger, name, fansTotal, headshot) values (%s,%s,%s,%s)'
            params = (item['blogger'], item['name'], item['fansTotal'], item['headshot'])
            self.db.otherOprate(sql, params=params)

        elif isinstance(item, SinaGroupInfo):
            print(item, 'group')
            db = sqlUtil.DBUtil()
            sql = 'INSERT INTO groupname(blogger, groupName) values (%s,%s)'
            params = (item['blogger'], item['group'])
            self.db.otherOprate(sql, params=params)

        elif isinstance(item, SinaWeiBoInfos):
            print(item, 'weibo')
            sql = 'INSERT INTO weibo(blogger, content, comeFrom, goodNumber, transmitNumber, commentNumber) ' \
                  'VALUES (%s, %s, %s, %s ,%s, %s)'
            params = (item['blogger'], item['content'], item['comeFrom'], item['goodNumber'], item['transmitNumber'],
                      item['commentNumber'])
            self.db.otherOprate(sql, params=params)

        return item

    def close_spider(self, spider):
        self.db.close()

