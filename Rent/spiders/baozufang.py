import time

import scrapy
from datetime import datetime
from ..utils.send_Email import sendMail
from configparser import ConfigParser
import os
'''
问题一：第二次请求被屏蔽
    debug：打开settings里的LOG_LEVEL='DEBUG',查看输出
    原因：allowed_domains里的url才会被允许访问 
    解决：注释掉该类变量

问题二：第三次请求被屏蔽
    原因：Scrapy提供了一个内置的重复请求过滤器，用于根据网址过滤重复的请求。
    解决：方法1：
            自定义一个过滤器,然后在settings里面使用：DUPEFILTER_CLASS = 'scraper.duplicate_filter.CustomFilter'
          方法2：
            Request对象的dont_filter = True
'''
class BaozufangSpider(scrapy.Spider):
    name = 'baozufang'
    # allowed_domains = ['211.145.35.3:7004']  # 定义这个 第二次请求会被屏蔽
    # start_urls = ['http://211.145.35.3:7004/article/b02e7e29e33642f789e4d1e41db08b7d/1/10']

    flag = 0
    last_time = datetime.now()

    def start_requests(self):
        urls = ['http://211.145.35.3:7004/article/b02e7e29e33642f789e4d1e41db08b7d/1/10']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse2)

    def parse(self, response):
        title = response.xpath('/html/body/div[2]/div/div/div/div[2]/div[3]/ul/li[1]/a/div[2]/h2/text()').get()
        print('title:',title)
        month = response.xpath('/html/body/div[2]/div/div/div/div[2]/div[3]/ul/li[1]/a/div[1]/span[2]/text()').get()
        print('month:',month)

        if '保障' in title and '5月' in month:
            # 给我发邮件
            print("请注意保租房申请！")

            if BaozufangSpider.flag == 0:
                # 第一次发送邮件
                print('第一次发送邮件')
                sendMail("保租房申请已经开通,请及时关注！","保租房",'hans_q','hans_q','2253559277@qq.com')
                BaozufangSpider.flag = 1
            else:
                time.sleep(20*60) # 如果已经发送过,那就降低查询频率
                now = datetime.now()
                delta = (now-BaozufangSpider.last_time).seconds
                if delta > 1*60*60:
                    # 离上一次发邮件过去1小时, 再次发邮件
                    print('离上一次发邮件过去1小时, 再次发邮件')
                    sendMail("保租房申请已经开通,请及时关注！", "保租房", 'hans_q', 'hans_q', '2253559277@qq.com')
                    BaozufangSpider.last_time = now

        else:
            print("公告还未发出,请持续关注...")

        # 间隔30秒,再次访问
        time.sleep(30)
        yield scrapy.Request(url=BaozufangSpider.start_urls[0], callback=self.parse, dont_filter=True)

    def parse2(self, response):
        '''
        请求一次,放在github Action里面运行. (因为github action每个job运行时间有限制,不能循环)
        :param response:
        :return:
        '''
        title = response.xpath('/html/body/div[2]/div/div/div/div[2]/div[3]/ul/li[1]/a/div[2]/h2/text()').get()
        print('title:',title)
        month = response.xpath('/html/body/div[2]/div/div/div/div[2]/div[3]/ul/li[1]/a/div[1]/span[2]/text()').get()
        print('month:',month)

        if '保障' in title and '5月' in month:
            # 给我发邮件
            print("请注意保租房申请！")
            con = ConfigParser()
            BASE_DIR = os.path.dirname(__file__) # 配置文件夹的目录 Rent/rent/spider
            cfg_path = os.path.join(BASE_DIR ,'..','..','scrapy.cfg') # Rent/scrapy.cfg

            con.read(cfg_path,'utf-8')
            flag = con.get('settings','flag')

            if flag == '0':
                # 第一次发送邮件
                print('第一次发送邮件')
                sendMail("保租房申请已经开通,请及时关注！","保租房",'hans_q','hans_q','2253559277@qq.com')
                con.set('settings','flag','1')
                con.set('settings', 'last_time', str(datetime.now().timestamp()))
            else:
                timestamp = float(con.get('settings', 'last_time'))
                last_time = datetime.fromtimestamp(timestamp)
                now = datetime.now()
                delta = (now-last_time).seconds
                if delta > 1*60*60:
                    # 离上一次发邮件过去1小时, 再次发邮件
                    print('离上一次发邮件过去1小时, 再次发邮件')
                    sendMail("保租房申请已经开通,请及时关注！", "保租房", 'hans_q', 'hans_q', '2253559277@qq.com')
                    con.set('settings', 'last_time', str(now.timestamp()))

            with open(cfg_path, "w+") as f:
                con.write(f)
        else:
            print("公告还未发出,请持续关注...")
