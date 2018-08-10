# -*- coding: utf-8 -*-

import scrapy

# 根据所需的字段，在资料库中创建表格
class SinaItem(scrapy.Item):
    # 博主所关注的人员相关信息
    blogger = scrapy.Field()
    attentionLink = scrapy.Field()
    name = scrapy.Field()
    fansTotal = scrapy.Field()
    headshot = scrapy.Field()

class SinaFansItem(scrapy.Item):
    blogger = scrapy.Field()
    # 博主粉丝的昵称，粉丝数量，以及粉丝头像链接
    name = scrapy.Field()
    fansTotal = scrapy.Field()
    headshot = scrapy.Field()

class SinaWeiBoInfos(scrapy.Item):
    # 该博主所发的博文的信息、发布源，点赞人数、转发人数、评论人数
    blogger = scrapy.Field()
    content = scrapy.Field()
    comeFrom = scrapy.Field()
    goodNumber = scrapy.Field()
    transmitNumber = scrapy.Field()
    commentNumber = scrapy.Field()

class SinaGroupInfo(scrapy.Item):
    # 该博主对于关注对象的分组情况
    blogger = scrapy.Field()
    group = scrapy.Field()