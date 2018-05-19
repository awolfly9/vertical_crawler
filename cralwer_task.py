# -*- coding=utf-8 -*-

import json
import re
from collections import namedtuple
from web.vertical.models import Seed


class CrawlTask(object):
    def __init__(self, seed_id):
        super().__init__()
        self.init(seed_id)

    def init(self, seed_id):
        self.seed = Seed.objects.filter(id = seed_id).first()
        self.crawler_json_obj = json.loads(self.seed.rule_data)
        self.crawler_text_obj = self.seed.rule_data

        # with open('config.json', 'r') as f:
        #     text = f.read()
        #     self.crawler_json_obj = json.loads(text)
        #     self.crawler_text_obj = text
        # print(self.crawler_json_obj)

        self.crawler = json.loads(self.seed.rule_data)
        # print(crawler)
        # for field in crawler._fields:
        #     setattr(self, field, getattr(crawler, field))

    def _json_object_hook(self, d):
        return namedtuple('crawler', d.keys())(*d.values())

    def _load_from_json(self):
        return json.loads(
            self.crawler_text_obj,
            object_hook = self._json_object_hook
        )

    @property
    def init_urls(self):
        seed_init = self.crawler.get('seed_init', {})
        init_type = seed_init.get('init_type')
        if init_type == 'pyfunc':
            code = seed_init.get('init_info')
            exec(code, globals())
            urls = init_func()  # TODO...
            print("urls:%s" % urls)
            return []
        elif init_type == 'template':
            return
        elif init_type == 'list':
            return seed_init.get('init_info')

    @property
    def add_pages(self):
        return self.crawler.get('add_pages', [])

    @property
    def seed_init(self):
        return self.crawler.get('seed_init', {})


def extract_json_body(extract_fields, root):
    slocator = extract_fields.slocator
    val = []
    if hasattr(extract_fields, "bfields"):
        bfields = extract_fields.bfields
        for section in extract_json_field(root, slocator):
            section_val = {}
            for bfield in bfields._fields:
                section_val[bfield] = extract_json_field(section, getattr(bfields, bfield))
            val.append(section_val)
    else:
        val = extract_json_field(root, slocator)
    return val


def extract_json_field(jsond, locator):
    ks = locator.split(".")
    val = jsond
    for k in ks:
        m = re.match(r'\[(\d+)\]', k)
        if m:
            index = int(m.groups()[0])
            val = val[index]
        else:
            val = val[k]
    return val


if __name__ == '__main__':
    task = CrawlTask()
    print(dir(task))

    task.init()
    print(dir(task))
    print('seed:%s' % str(task.seed))
    print('seed:%s' % task.seed.init_urls)
    print('seed:%s' % type(task.seed.init_urls))
