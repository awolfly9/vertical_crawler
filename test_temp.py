# -*- coding=utf-8 -*-
#
from jinja2 import Template

template = Template('http://awolfly9.com/{{article}}')

print(dir(template))
x = template.render(article = 'faaaaaa')
print(x)
print(type(x))

#
# import requests
# from urllib.parse import urljoin
#
# print(urljoin('http://awolfly9.com/article/tianjin', '/article/ddd'))
#
# func = '''
#

# '''
#
# print(exec(func))
#
# import sys
#
#
# #
# code = """
# def f(x):
#     # # x = x + 1
#     # # return x
#     x = []
#     x.append('a')
#     x.append('b')
#     x.append('c')
#     return x
# print ('This is my output.')
# """
#
# exec(code)
#
# r = f(3)
# # print(r.status_code)
# print(r)

code = '''
def init_func():
    urls = [
        'http://api.jiefu.tv/app2/api/bq/article/detail.html?id=4674',
        'http://api.jiefu.tv/app2/api/bq/article/detail.html?id=4674',
        'http://api.jiefu.tv/app2/api/bq/article/detail.html?id=4674',
    ]
    return urls
'''


class Test(object):
    def init(self):
        print('code:%s' % code)
        # l, g = locals().copy(), globals().copy()
        exec(code, globals())
        x = init_func()
        print(x)


t = Test()
t.init()

#
# if __name__ == '__main__':
#     t = Test()
#     t.init()
