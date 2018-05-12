# -*- coding=utf-8 -*-

import json
import re
from collections import namedtuple
from web.vertical.models import Seed, Result


class CrawlerSave(object):
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.seed = task.seed

    def save(self, crawler_url, origin_data, extract_data):
        res = Result(crawler_url = crawler_url, origin_data = origin_data, extract_data = extract_data,
                     seed_id = self.seed.id, crawler_name = self.seed.name)
        res.save()
