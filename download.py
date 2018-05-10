# -*- coding=utf-8 -*-

import requests


class Download(object):
    def __init__(self, task, *args, **kwargs):
        self.task = task

        self.proxies = {
            'http': '10.3.14.61:8080',
            'https': '10.3.14.61:3128',
        }

    def download(self, task, url):
        print('download url:%s' % url)
        r = requests.get(url = url, proxies = self.proxies)
        url_path = url.replace('/', '_')
        with open('log/%s.html' % url_path[-15:], 'w') as f:
            f.write(r.text)
        if r.status_code == 200:
            status = True
        else:
            status = False
        return status, r.text
