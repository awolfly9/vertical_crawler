# -*- coding=utf-8 -*-

import re
import json
import sys
import better_exceptions
import os
import django

sys.path.append(os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings'
django.setup()

from urllib.parse import urljoin
from cralwer_save import CrawlerSave
from cralwer_task import CrawlTask
from download import Download
from lxml.html import fromstring
from jinja2 import Template

better_exceptions.hook()


class Crawler(object):
    def __init__(self, seed_id):
        # 初始化抓取任务
        self.task = CrawlTask(seed_id)
        self.save = CrawlerSave(self.task)
        # 初始化下载下载接口
        self.download = Download(self.task)

    def run_page_actions(self):
        for url in self.task.init_urls:
            print('init_url:%s' % url)
            status, text = self.download.download(self.task, url)
            print('run_page_actions  status:%s' % status)
            # 开始处理对页面的请求，提取元素进入下一页 or 直接提取数据
            for action in self.task.add_pages:
                self.run_extract_action(action, text, url)

    def run_extract_action(self, action, text, url, **kwargs):
        next = action.get('next', None)
        if next is not None:
            # 提取元素进入下一页
            if next.get('type', None) == 'xpath':
                self.extract_with_xpath(action, text, url, **kwargs)
            elif next.get('type', None) == 'json':
                self.extract_with_json(action, text, url, **kwargs)
            elif next.get('type', None) == 're':
                self.extract_with_re(action, text, url, **kwargs)
        else:  # 到达最后一页，开始提取数据
            # 提取数据
            extract_field = action.get('extract_field', None)
            if extract_field is not None:
                if action.get('extract_type') == 'xpath':
                    body = fromstring(text)
                    results = {}
                    extract_field = action.get('extract_field')
                    # 循环提取字段
                    for key, field_value in extract_field.items():
                        value = body.xpath(key, smart_strings = False)
                        if field_value not in results:
                            results[field_value] = []
                            results[field_value].extand(value)
                        else:
                            results[field_value].extand(value)
                    self.save.save(url, '', results)
                elif action.get('extract_type', None) == 'json':
                    body = json.loads(text)
                    extract_field = action.get('extract_field')
                    results = {}
                    self.get_fields(body, extract_field, results)
                    self.save.save(url, text, results)

    # 通过 xpath 解析数据
    def extract_with_xpath(self, action, text, url, **kwargs):
        body = fromstring(text)
        next = action.get('next')
        next_field = next.get('next_field', {})
        for key, field_value in next_field.items():
            results = body.xpath(key, smart_strings = False)
            for result in results:
                add_pages = action.get('add_pages')
                for next_action in add_pages:
                    next_url = urljoin(url, result)
                    # 过滤掉不相关的 URL，这里使用正则
                    if self.url_filter(next.get('next_url_regex'), next_url) is None:
                        continue
                    print('action:%s next_url:%s' % (action.get('name'), next_url))
                    status, text = self.download.download(self.task, next_url)
                    self.run_extract_action(next_action, text, next_url)

    # 解析 json 拿到下一个入口
    def extract_with_json(self, action, text, url, **kwargs):
        body = json.loads(text)
        next = action.get('next', {})
        next_field = next.get('next_field', {})
        next_bodys = []
        next_bodys.append(body)
        print('next_field:%s' % next_field)
        results = {}  # 查找输出结果，这里先不要考虑太复杂
        self.get_fields(body, next_field, results)
        print('results:%s' % results)
        template = Template(next.get('next_url_temp'))
        min_len = sys.maxsize
        key_list = results.keys()  # TODO... 这里应该定向获取到某一个对象的长度
        for key, value_list in results.items():
            min_len = min(min_len, len(value_list))

        add_pages = action.get('add_pages', None)
        if add_pages is None:
            # 没有下一步动作，应该提取数据
            pass
        else:  # 提取下一步的 URL，进入下一步流程
            for next_action in add_pages:
                for i in range(0, min_len):
                    kwargs = {}
                    for key in key_list:
                        kwargs[key] = results[key][i]
                    next_url = template.render(kwargs)
                    print('url:%s' % url)
                    if self.url_filter(next.get('next_url_regex'), next_url) is None:
                        continue
                    print('action:%s next_url:%s' % (action.get('name'), next_url))
                    status, text = self.download.download(self.task, next_url)
                    self.run_extract_action(next_action, text, next_url)

    # key 始终是要获取的值
    # value 命名
    # body json
    # field 要采集的数据的 缩小版 json 格式
    # results 采集到的数据最终会存储在 results
    def get_fields(self, body, field, results):
        def get_field():
            if isinstance(field_value, list):
                for value in field_value:
                    self.get_fields(new_body, value, results)
            elif isinstance(field_value, dict):
                self.get_fields(new_body, field_value, results)
            elif isinstance(field_value, str):
                if field_value not in results:
                    results[field_value] = []
                    results[field_value].append(new_body)
                else:
                    results[field_value].append(new_body)

        for key, field_value in field.items():
            if isinstance(body, dict):
                new_body = body.get(key)
                get_field()
            elif isinstance(body, list):
                for item in body:
                    new_body = item.get(key)
                    get_field()

    # 通过正则拿到下一个入口
    def extract_with_re(self, action, text, url, **kwargs):
        pass

    def url_filter(self, next_url_regex, next_url):
        search = re.search(next_url_regex, next_url, re.I)
        if search:
            return next_url
        else:
            return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        seed_id = sys.argv[1]
    else:
        seed_id = 2

    crawler = Crawler(seed_id = seed_id)
    crawler.run_page_actions()

'''
"userView": {
                "id": "user_id",
                "nickName": "user_name"
              },
              "itemView": {
                "createTime": "createTime"
              },
'''
# regex = 'http://api.jiefu.tv/app2/api/bq/article/detail.html?id=(\\d+)'
# text = 'http://api.jiefu.tv/app2/api/bq/article/detail.html?id=25715'
