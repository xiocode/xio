#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from joke.tables import tb_joke

__author__ = 'Tony.Shao'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

from gevent import monkey

monkey.patch_all()
import re
from gevent.pool import Group
from gevent.queue import JoinableQueue
import gevent
import traceback

proxies = {
    'http': '127.0.0.1:8087'
}

PROXY_IP = '127.0.0.1'

headers = {
    'X-Forwarded-For': '%s, 127.0.0.1, 192.168.0.1' % PROXY_IP,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.43 Safari/536.11'
}

crawler_group = Group()
crawler_queue = JoinableQueue()

#通过代理抓取用户Timeline
from geventhttpclient import HTTPClient
from geventhttpclient import URL

_ver = sys.version_info
#: Python 2.x?
is_py2 = (_ver[0] == 2)
#: Python 3.x?
is_py3 = (_ver[0] == 3)

def _http_call(url):
    try:
        url = URL(url=url)
        client = HTTPClient.from_url(url, concurrency=100)
        uri = url.request_uri
        resp = client.get(uri, headers=headers)
        return resp
    except Exception:
        print traceback.format_exc()
        return None

def _read_body(resp, encoding='UTF-8'):
    if is_py2:
        return unicode(resp.read(), encoding)
    if is_py3:
        return str(resp.read(), encoding)


url = 'http://www.jokeji.cn/list_%d.htm'
BASE_URL = 'http://www.jokeji.cn'
crawler_outer_pattern = re.compile(r'<a\s+href="([^"]+?)"target="_blank"\s+>([^<]+?)</a>')
crawler_inner_pattern = re.compile(r'<span id="text110">(.*?)</span>', re.S)

def crawler_boss():
    for x in xrange(1, 300):
        crawler_queue.put(url % x)

    for x in xrange(10):
        crawler_group.spawn(crawler_worker)

    crawler_group.join()


def crawler_worker():
    while not crawler_queue.empty():
        try:
            url = crawler_queue.get()
            print url
            outer_resp = _http_call(url)
            outer_text = _read_body(outer_resp, encoding='gb2312')
            crawler_outer_parser(outer_text)
        except Exception:
            print traceback.format_exc()
        finally:
            crawler_queue.task_done()
            gevent.sleep(0.0)


def crawler_outer_parser(outer_text):
#    print outer_text
    crawler_data = {}
    outer_datas = crawler_outer_pattern.findall(outer_text)
    for url, title in outer_datas:
        try:
            resp = _http_call(BASE_URL + url)
            crawler_data['title'] = title
            inner_text = _read_body(resp, encoding='gb2312')
            crawler_data.update(crawler_inner_parser(inner_text))
            suppliers_info = tb_joke(**crawler_data)
            print url
            suppliers_info.save()
            print '已经抓取 ' + url
        except Exception as e:
            print traceback.format_exc()


def crawler_inner_parser(inner_text):
    crawler_data = {}
    try:
        inner_data = crawler_inner_pattern.findall(inner_text)
        content = strip_tags(inner_data[0].strip())
        crawler_data['content'] = content
    except IndexError as e:
        print inner_text
    return crawler_data


def strip_tags(html):
    return re.sub('<[^<]+?>', ' ', html)


def site_crawler():
    crawler_boss()


if __name__ == '__main__':
    print _http_call('http://www.163.com').read()


