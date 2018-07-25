# -*- coding: utf-8 -*-
'''
    Author : Ribbon Huang
    Date: 2018-07-24
'''
import scrapy
from sina.items import *
import re

class SinaSpiderSpider(scrapy.Spider):
    name = 'sina_spider'
    allowed_domains = ['weibo.cn']
    start_urls = [
        5235640836, 5676304901, 5871897095, 2139359753, 5579672076, 2517436943, 5778999829, 5780802073, 2159807003,
        1756807885, 3378940452, 5762793904, 1885080105, 5778836010, 5722737202, 3105589817, 5882481217, 5831264835,
        2717354573, 3637185102, 1934363217, 5336500817, 1431308884, 5818747476, 5073111647, 5398825573, 2501511785,
    ]
    # start_urls = [5235640836]
    startList = set(start_urls)
    overList = set()

    def start_requests(self):
        while self.startList.__len__():
            urlId = self.startList.pop()
            self.overList.add(urlId)
            urlId = str(urlId)
            # 该博客所关注的其他博主相关信息链接
            urlAttention = "https://weibo.cn/%s/follow" % urlId
            # 关注该博主的粉丝的相关信息链接
            urlFans = "https://weibo.cn/%s/fans" % urlId
            # 该博主对关注的其他博主的分组详情
            urlGroupName = "https://weibo.cn/attgroup/opening?uid=%s" % urlId
            # 该博主所发博客的所有相关信息
            urlWeiBo = "https://weibo.cn/%s/profile?filter=1&page=1" % urlId

            # 测试时候使用的网页
            # 'http://weibo.com/1934363217/profile?topnav=1&wvr=6&is_all=1'
            # 'https://weibo.cn/5235640836/follow'

            # 根据所要爬取的不同内容。来进行调用筛选函数
            yield scrapy.Request(url=urlAttention, meta={'blogger':urlId}, callback=self.parseAttention)
            yield scrapy.Request(url=urlFans, meta={'blogger':urlId}, callback=self.parseFans)
            yield scrapy.Request(url=urlGroupName, meta={'blogger':urlId}, callback=self.parseGroupName)
            yield scrapy.Request(url=urlWeiBo, meta={'blogger':urlId}, callback=self.parseWeiBo)

    def parseAttention(self, response):
        pattern = '<td valign[\s\S]*?<a[\s\S]*?<img src="(.*?)"[\s\S]*?<td valign="top"><a href="([\s\S]*?)">' \
                  '([\s\S]*?)</a>[\s\S]*?<br/>([\s\S]*?)<br'
        attentions = re.findall(pattern, response.text)
        # 将博主所关注的其他博主的相关信息存成字典的形式，再组合成列表传参给管道文件。管道文件需要进行列表遍历存入资料库中
        for i in attentions:
            attentionItem = SinaItem()
            attentionItem['blogger'] = response.meta['blogger']
            attentionItem['attentionLink'] = i[1]
            attentionItem['name'] = i[2]
            attentionItem['fansTotal'] = i[3]
            attentionItem['headshot'] = i[0]
            _id = i[1].split('/')[-1]
            if _id not in self.overList and _id not in self.startList:
                self.startList.add(_id)
            # print(attentionItem)
            yield attentionItem

        nextpage = re.findall('<div><a href="([\s\S]*?)">下页</a>', response.text)
        nextpage = r'https://weibo.cn' + nextpage[0]
        if nextpage:
            yield scrapy.Request(url=nextpage, callback=self.parseAttention, meta={'blogger':response.meta['blogger']})
        # print(item)
        # return item

    def parseFans(self, response):
        # print(response.text)
        pattern = '<td valign[\s\S]*?<a[\s\S]*?<img src="(.*?)"[\s\S]*?<td valign="top"><a href="([\s\S]*?)">' \
                  '([\s\S]*?)</a><br/>([\s\S]*?)<br/><a'
        fans = re.findall(pattern, response.text)
        # 将粉丝界面所需要的信息，每个粉丝信息组成字典，再形成列表传给管道。管道需要遍历的方式来进行存储到资料库中
        for fan in fans:
            fansItem = SinaFansItem()
            fansItem['headshot'] = fan[0]
            fansItem['fansTotal'] = fan[3]
            fansItem['name'] = fan[2]
            fansItem['blogger'] = response.meta['blogger']
            _id = fan[1].split('/')[-1]
            if _id not in self.overList and _id not in self.startList:
                self.startList.add(_id)
            yield fansItem
        # print(item)
        nextpage = re.findall('<div><a href="([\s\S]*?)">下页</a>', response.text)
        nextpage = r'https://weibo.cn' + nextpage[0]
        # print(nextpage)
        if nextpage:
            yield scrapy.Request(url=nextpage, callback=self.parseFans, meta={'blogger':response.meta['blogger']})

    def parseGroupName(self, response):
        # print(response.text)
        # 把用户所有的分组进行查找，只有一页，所以不需要翻页..但是第一个组比较特别，所以需要两段正则进行查找。
        # pattern = '<div class="c"><a href=[\s\S]*?>([\s\S]*?)</a>'
        # groupsItem = SinaGroupInfo()
        # groupsItem['blogger'] = response.meta['blogger']
        # groupsItem['group'] = re.findall(pattern, response.text)[0]
        # items.append(groupsItem)
        pattern = '<div class="s"></div><a href=[\s\S]*?>([\s\S]*?)</a>|<div class="c"><a href=[\s\S]*?>' \
                  '([\s\S]*?)</a>'
        groups = re.findall(pattern, response.text)
        for group in groups:
            groupsItem = SinaGroupInfo()
            groupsItem['blogger'] = response.meta['blogger']
            groupsItem['group'] = group[0]
            if groupsItem['group'] == '':
                continue
            yield groupsItem

        # print(item)

    def parseWeiBo(self, response):
        # print(response.text)
        # 将博主所发的所有博文进行获取，通过管道进入资料库。 定位 下一页 是否存在来进行翻页
        pattern = '<div><span class="ctt">([\s\S]*?)<[\s\S]*?<a[\s\S]*?>([\s\S]*?)</a>[\s\S]*?<a[\s\S]*?>' \
                  '([\s\S]*?)</a[\s\S]*?<a[\s\S]*?>([\s\S]*?)</a>[\s\S]*?<span[\s\S]*?>([\s\S]*?)</span>'
        weibos = re.findall(pattern, response.text)
        for weibo in weibos:
            weiBoItem = SinaWeiBoInfos()
            weiBoItem['blogger'] = response.meta['blogger']
            weiBoItem['content'] = weibo[0]
            weiBoItem['comeFrom'] = weibo[4]
            weiBoItem['goodNumber'] = weibo[1]
            weiBoItem['transmitNumber'] = weibo[2]
            weiBoItem['commentNumber'] = weibo[3]
            yield weiBoItem
        # print(item)
        nextpage = re.findall('<div><a href="([\s\S]*?)">下页</a>', response.text)
        nextpage = r'https://weibo.cn' + nextpage[0]
        if re.search('amp;',nextpage):
            # 正则处理所获取的网页信息，scrapy获取下来会多一个 amp; 故网页时刻保持在第一页
            nextpage = re.sub('amp;', '', nextpage)
            # 'https://weibo.cn/5235640836/profile?filter=1&amp;page=2'
            # 'https://weibo.cn/5235640836/profile?filter=1&page=2'
        # print(item)
        if nextpage:
            yield scrapy.Request(url=nextpage, callback=self.parseWeiBo, meta={'blogger': response.meta['blogger']})

