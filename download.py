# -*- coding=utf-8 -*-

import requests


class Download(object):
    def __init__(self):
        self.proxies = {
            'http': '10.3.14.61:8080',
            'https': '10.3.14.61:3128',
        }

    def download(self, url):
        r = requests.get(url = url, proxies = self.proxies)
        if r.status_code == 200:
            status = True
        else:
            status = False
        return status, r.text
