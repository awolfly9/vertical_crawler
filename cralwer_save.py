# -*- coding=utf-8 -*-

import json
import re
from collections import namedtuple
from web.vertical.models import Seed, Result

import hashlib


def hash_uint64(raw_val):
    '''
    >>> hash_uint64('')
    15284527576400310788L
    '''
    if isinstance(raw_val, str):
        raw_val = raw_val.encode()
    val = hashlib.md5(raw_val).hexdigest()
    return int(val[:16], 16)


class CrawlerSave(object):
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.seed = task.seed

    def save(self, crawler_url, origin_data, extract_data):
        info = {
            'crawler_url': crawler_url,
            'origin_data': origin_data,
            'extract_data': extract_data,
            'seed_id': self.seed.id,
            'crawler_name': self.seed.name,
        }
        url_id = hash_uint64(crawler_url)
        print('url_id:%s' % url_id)
        Result.objects.get_or_create(url_id = url_id, defaults = info)
