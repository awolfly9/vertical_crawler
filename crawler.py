# -*- coding=utf-8 -*-

import re
import json
import better_exceptions

from urllib.parse import urljoin
from cralwer_task import CrawlTask
from download import Download
from lxml.html import fromstring

better_exceptions.hook()


class Crawler(object):
    def __init__(self, seed_id):
        # 初始化抓取任务
        self.task = CrawlTask()
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
        if action.get('next_url_regex', None) is not None:  # 提取元素进入下一页
            if action.get('next_extract_type', None) == 'xpath':
                self.extract_with_xpath(action, text, url, **kwargs)
            elif action.get('next_extract_type', None) == 'json':
                self.extract_with_json(action, text, url, **kwargs)
            elif action.get('next_extract_type', None) == 're':
                self.extract_with_re(action, text, url, **kwargs)
        else:  # 到达最后一页，开始提取数据
            # 提取数据
            if hasattr(action, 'extract_field') and len(action.extract_field) > 0:
                if action.extract_type == 'xpath':
                    body = fromstring(text)
                    info = {}
                    extract_field = action.extract_field
                    # 循环提取字段
                    for field_name in extract_field._fields:
                        rule = getattr(extract_field, field_name)
                        value = body.xpath(rule, smart_strings = False)
                        print('action name:%s field_name:%s value:%s' % (action.name, field_name, value))
                        info[field_name] = value

    # 通过 xpath 解析数据
    def extract_with_xpath(self, action, text, url, **kwargs):
        body = fromstring(text)
        results = body.xpath(action.next_field, smart_strings = False)
        for result in results:
            if hasattr(action, 'add_pages') == False or len(action.add_pages) <= 0:
                # 没有下一步动作，应该提取数据
                continue
            else:  # 提取下一步的 URL，进入下一步流程
                for next_action in action.add_pages:
                    next_url = urljoin(url, result)
                    # 过滤掉不相关的 URL，这里使用正则
                    if self.url_filter(action, next_url) is None:
                        continue
                    print('action:%s next_url:%s' % (action.name, next_url))
                    status, text = self.download.download(self.task, next_url)
                    self.run_extract_action(next_action, text, url)

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
        # for i, field in enumerate(next_field._fields):
        #     field_value = getattr(next_field, field)
        #     result = body.get(field)
        #     if isinstance(field_value, list):
        #         for item in field_value:
        #             for field in item._fields:
        #                 print('field__:%s' % field)
        # print('field:%s field_value:%s' % (field, field_value))
        # new_next_bodys = []
        # for next_body in next_bodys:
        #     new_next_bodys.extend(self.get_field(next_body, field))

        # self.get_field(body, field)

        # print(next_bodys)

    # key 始终是要获取的值
    # value 命名
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
                else:
                    results[field_value].append(new_body)

        for key, field_value in field.items():
            if isinstance(body, dict):
                new_body = body.get(key)

                # if isinstance(field_value, list):
                #     for value in field_value:
                #         self.get_fields(new_body, value, results)
                # elif isinstance(field_value, dict):
                #     self.get_fields(new_body, field_value, results)
                # elif isinstance(field_value, str):
                #     if field_value not in results:
                #         results[field_value] = []
                #     else:
                #         results[field_value].append(new_body)
                get_field()
            elif isinstance(body, list):
                for item in body:
                    new_body = item.get(key)

                    get_field()

    # 通过正则拿到下一个入口
    def extract_with_re(self, action, text, url, **kwargs):
        pass

    def url_filter(self, action, next_url):
        search = re.search(action.next_url_regex, next_url)
        if search:
            return next_url
        else:
            return None


if __name__ == '__main__':
    crawler = Crawler(seed_id = -1)
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
