# -*- coding=utf-8 -*-

from jinja2 import Template

template = Template('Hello {{ name }}!')

print(dir(template))
x = template.render(dsafdsa = 'John Doe', fakdsjl = 'fjksdjlk', name = 'faaaaaa')
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
x = []
x.append('a')
x.append('b')
x.append('c')
print(x)
# '''
#
# print(exec(func))
#
# import sys
#
# # import StringIO
#
# # create file-like string to capture output
# # codeOut = StringIO.StringIO()
# # codeErr = StringIO.StringIO()
#
# code = """
# def f(x):
#     r = requests.get('http://awolfly9.com/')
#     return r
#     # # x = x + 1
#     # # return x
#     # x = []
#     # x.append('a')
#     # x.append('b')
#     # x.append('c')
#     # return x
# print ('This is my output.')
# """
#
# # capture output and errors
# # sys.stdout = codeOut
# # sys.stderr = codeErr
#
# exec(code)
#
# # restore stdout and stderr
# # sys.stdout = sys.__stdout__
# # sys.stderr = sys.__stderr__
#
# r = f(3)
# print(r.status_code)
# print(r.text)
# #
# # s = codeErr.getvalue()
# #
# # print("error:\n%s\n" % s)
# #
# # s = codeOut.getvalue()
# #
# # print("output:\n%s" % s)
# #
# # codeOut.close()
# # codeErr.close()
