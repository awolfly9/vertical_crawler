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
        seed_init = self.task.seed_init
        for url in self.task.init_urls:
            print('init_url:%s' % url)
            status, text = self.download.download(self.task, url)
            print('run_page_actions  status:%s' % status)

            # # 首先提取上一页应该提取的字段
            # extract_fields = seed_init.get('extract_fields')
            # #
            #
            # # 开始处理对页面的请求，提取元素进入下一页 or 直接提取数据
            # page_actions = self.task.seed_init.get('add_pages')
            # for action in page_actions:
            #     print('URL:%s  action:%s' % (url, action))
            #     self.run_extract_action(action, text, url)
            self.page_parse(seed_init, url, text)

    def page_parse(self, action, url, text, **kwargs):
        # 首先提取上一页应该提取的字段
        extract_fields = action.get('extract_fields')
        type = extract_fields.get('type')
        if type == 'saveall':
            self.save.save(url, text, '')
        #

        # 开始处理对页面的请求，提取元素进入下一页 or 直接提取数据
        page_actions = action.get('add_pages', [])
        for action in page_actions:
            print('URL:%s  action:%s' % (url, action))
            self.run_extract_action(action, text, url)

    def run_extract_action(self, action, text, url, **kwargs):
        print('action name:%s' % action.get('action_name'))
        next = action.get('next', {})
        # 提取元素进入下一页
        type = next.get('type', None)
        fields = next.get('fields', None)
        next_url_list = []  # 返回一个 URL 列表，这里目前只支持一个字段
        if type == 'xpath':
            next_url_list = self.extract_with_xpath(action, text, url, **kwargs)
        elif type == 'json':
            next_url_list = self.extract_with_json(action, text, url, **kwargs)
        elif type == 're':
            next_url_list = self.extract_with_re(action, text, url, **kwargs)
        elif type == 'pyfunc':
            pass

        print('next_url_list:%s' % next_url_list)
        for next_url in next_url_list:
            url_regex = next.get('url_regex')
            # 过滤掉不相关的 URL，这里使用正则
            if self.url_filter(url_regex, next_url) is None:
                continue

            print('action:%s next_url:%s' % (action.get('action_name'), next_url))
            status, text = self.download.download(self.task, next_url)
            self.page_parse(action, next_url, text)

    def extract_url(self, action, text, url, **kwargs):
        next = action.get('next', {})
        type = next.get('type', None)
        fields = next.get('fields', None)
        next_url_list = []  # 返回一个 URL 列表，这里目前只支持一个字段
        if type == 'xpath':
            next_url_list = self.extract_with_xpath(action, text, url, **kwargs)
        elif type == 'json':
            next_url_list = self.extract_with_json(action, text, url, **kwargs)
        elif type == 're':
            next_url_list = self.extract_with_re(action, text, url, **kwargs)
        elif type == 'pyfunc':
            pass
        return next_url_list

    # 通过 xpath 解析数据
    def extract_with_xpath(self, action, text, url, **kwargs):
        body = fromstring(text)
        next = action.get('next', {})
        fields = next.get('fields', {})  # TODO...
        fields_dict = json.loads(fields)
        url_list = []
        for key, field_value in fields_dict.items():
            print('field_value:%s' % field_value)
            url_temp = next.get('url_temp')
            print('url_temp:%s' % url_temp)
            results = body.xpath(key, smart_strings = False)
            for res in results:
                template = Template(url_temp)
                url = template.render(**{field_value: res})
                url_list.append(url)
        return url_list

    # 解析 json 拿到下一个入口
    def extract_with_json(self, action, text, url, **kwargs):
        body = json.loads(text)
        next = action.get('next', {})
        fields = next.get('fields', {})
        next_bodys = []
        next_bodys.append(body)
        fields_dict = json.loads(fields)
        results = {}  # 查找输出结果，这里先不要考虑太复杂
        self.get_fields(body, fields_dict, results)
        print('results:%s' % results)
        template = Template(next.get('url_temp'))
        min_len = sys.maxsize
        key_list = results.keys()  # TODO... 这里应该定向获取到某一个对象的长度
        for key, value_list in results.items():
            min_len = min(min_len, len(value_list))

        url_list = []
        for i in range(0, min_len):
            kwargs = {}
            for key in key_list:
                kwargs[key] = results[key][i]
            url = template.render(kwargs)
            url_list.append(url)
        return url_list

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

        if isinstance(field, list):
            for val in field:
                for key, field_value in val.items():
                    new_body = body.get(key)
                    get_field()
        elif isinstance(field, dict):
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
        seed_id = 24

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
