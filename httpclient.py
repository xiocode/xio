#!/usr/bin/env python
# -*- coding: utf-8 -*-
import chardet
import sys
import traceback

__author__ = 'Tony.Shao'

#通过代理抓取用户Timeline
from geventhttpclient import HTTPClient
from geventhttpclient import URL

proxies = {
    'http': '127.0.0.1:8087'
}
PROXY_IP = '127.0.0.1'
headers = {
    'X-Forwarded-For': '%s, 127.0.0.1, 192.168.0.1' % PROXY_IP,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.43 Safari/536.11'
}

_ver = sys.version_info
#: Python 2.x?
is_py2 = (_ver[0] == 2)
#: Python 3.x?
is_py3 = (_ver[0] == 3)

def _http_call(url):
    try:
        url = URL(url=url)
        client = HTTPClient.from_url(url, concurrency=20)
        uri = url.request_uri
        resp = client.get(uri, headers=headers)
        return resp
    except Exception:
        print traceback.format_exc()
        return None

http_call = _http_call

def _read_body(resp, encoding=None):
    content = resp.read()
    if encoding is None:
        encoding = chardet.detect(content)['encoding']
    if is_py2:
        return unicode(content, encoding=encoding)

read_body = _read_body
