# -*- coding: utf-8 -*-
import scrapy
from weather.weather.items import WeatherItem2

class WeekweatherspiderSpider(scrapy.Spider):
    name = 'weekweatherspider'
    allowed_domains = ['www.weather.com.cn']
    start_urls = ['http://www.weather.com.cn/textFC/macao.shtml']
    l = []
    custom_settings = {
        'ITEM_PIPELINES': {
            'weather.weather.pipelines.WeatherPipeline': 300,
        }
    }

    def parse(self, response):
        """爬取首页，获取各省各直辖市的链接"""
        city_list = response.xpath('//div[@class="lqcontentBoxheader"]//li/a/@href').extract()
        if city_list:
            for i in city_list:
                url = "http://www.weather.com.cn" + i
                yield scrapy.Request(url=url, callback=self.cityHandler)
            # url = "http://www.weather.com.cn/textFC/macao.shtml"
            # yield scrapy.Request(url=url, callback=self.cityHandler)
        else:
            print("首页各城市链接获取失败")

    def cityHandler(self, response):
        """获取进入各省会城市和直辖市的链接"""
        detail_link = response.xpath('//div[@class="conMidtab3"][1]/table/tr/td[2]/a/@href').extract()[0]
        if detail_link:
            # print(detail_link)
            yield scrapy.Request(url=detail_link, callback=self.detailHandler)
        else:
            print("各城市详情链接获取失败")

    def detailHandler(self, response):
        """获取各部分的内容"""
        temperature_2 = []
        day = []
        date_1 = []
        winddirection = []
        item_2 = WeatherItem2()
        # 获取七天的日期/时间列表
        date = response.xpath('//ul[@class="t clearfix"]/li/h1/text()').extract()
        for i in date:
            # print(i)
            if len(i) == 6:
                day.append(i[3:5])
                date_1.append(i[0:2])
            else:
                day.append(i[4:6])
                date_1.append(i[0:3])
        # 获取天气列表
        weather = response.xpath('//ul[@class="t clearfix"]/li/p[1]/text()').extract()
        # 获取气温列表
        temperature_1 = response.xpath('//ul[@class="t clearfix"]/li/p[@ class ="tem"]')
        temperature = temperature_1.xpath('string(.)').extract()
        # 获取风力强度列表
        windStrong = response.xpath('// ul[@class ="t clearfix"]/li/p[@class ="win"]/i/text()').extract()
        # 获取风向列表
        windDirection = response.xpath('//ul[@class="t clearfix"]/li/p[@class ="win"]/em/span[1]/@title').extract()
        for i in range(7):
            # print(i)
            winddirection.append(windDirection[i]+windStrong[i])
            # print(winddirection)
        # 获取对应城市的列表
        city_1 = response.xpath('//div[@class="crumbs fl"]/a[1]/text()').extract()
        city_2 = response.xpath('//div[@class="crumbs fl"]/a[2]/text()').extract()
        if city_1[0] in ["香港","北京","重庆","上海","天津","澳门"]:
            item_2["city"] = city_1
        else:
            item_2["city"] = city_2
        item_2["day"] = day
        item_2["date"] = date_1
        item_2["weather"] = weather
        for i in temperature:
            temperature_2.append(i[1:-1])
        item_2["temperature"] = temperature_2
        item_2["winddirection"] = winddirection
        # print(item_2,'------------------------------------')
        return item_2




