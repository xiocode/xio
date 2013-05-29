#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

from gevent import monkey

monkey.patch_all()

import requests
import re
from gevent.pool import Group
from gevent.queue import JoinableQueue
import gevent
import traceback
from tables import tb_20120924_cas_info

proxies = {
    'http': '127.0.0.1:8087'
}

PROXY_IP = '127.0.0.1'

headers = {
    'X-Forwarded-For': '%s, 127.0.0.1, 192.168.0.1' % PROXY_IP,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.43 Safari/536.11'
}

session = requests.session()

def _http_call(url):
    try:
        return session.get(url=url, headers=headers)
    except Exception:
        print traceback.format_exc()
        return None

cas_group = Group()
cas_queue = JoinableQueue()

next_page_pattern = re.compile(r'<a\s+href=\'([^\']+?)\'>\s+Next\s+</a>')
cas_outer_pattern = re.compile(
    r'<li><p\s+class="bw_line1"><a\s+href="([^"]+?)"\s+class="blue"\s+target="_blank">([^<]+?)</a></p>\s+<p\s+class="bw_line2"><a\s+href="[^"]+?"\s+class="blue"\s+target="_blank">([^<]+?)</a></p>.*?</li>',
    re.S)
cas_inner_pattern = re.compile(r'<td\s+align="right"\s+bgcolor="#F5FBFF"\s+class="blue">(.*?)</td>\s+<td\s+align="left">(.*?)</td>', re.S)
molecular_structure_img_pattern = re.compile(r'<img\s+SRC="([^"]+?)"')
cas_category_base_url = 'http://www.chemnet.com/cas/list/%d-1.html'
BASE_URL = 'http://www.chemnet.com'

def cas_boss():
    for x in xrange(1, 9):
        url = cas_category_base_url % x
        cas_queue.put(url)

    for x in xrange(10):
        cas_group.spawn(cas_worker)

    cas_group.join()


def cas_worker():
    while not cas_queue.empty():
        try:
            url = cas_queue.get()
            gevent.sleep()
            outer_resp = _http_call(url)
            outer_text = outer_resp.text
            next_page_url = next_page_pattern.findall(outer_text)
            if next_page_url:
                url = BASE_URL + next_page_url[0]
                cas_queue.put(url)
                print url
            cas_outer_parser(outer_text)

        except Exception:
            print traceback.format_exc()
        finally:
            cas_queue.task_done()


def cas_outer_parser(outer_text):
#    print outer_text
    outer_datas = cas_outer_pattern.findall(outer_text)
    for url, cas_id, product_name in outer_datas:
        cas_infos = {}
        cas_id = cas_id.strip()
        result = tb_20120924_cas_info.select().where(tb_20120924_cas_info.cas_id==cas_id).execute()
        if not result.cursor.rowcount:
            url = BASE_URL + url
            product_name = product_name.strip()
            resp = _http_call(url)
            cas_infos['product_name'] = product_name
            cas_infos['cas_id'] = cas_id
            cas_infos['url'] = url
            cas_infos.update(cas_inner_parser(resp.text))
            cas_info = tb_20120924_cas_info(**cas_infos)
            print url
            cas_info.save()


def strip_tags(html):
    return re.sub('<[^<]+?>', ' ', html)

def format_key(key):
    return '_'.join(key.lower().strip().split(' '))

def cas_inner_parser(inner_text):
    cas_info = {}
    inner_datas = cas_inner_pattern.findall(inner_text)
    for key, value in inner_datas:
        key = format_key(key)
        if key == 'molecular_structure':
            value = molecular_structure_img_pattern.findall(value)[0]
        value = strip_tags(value).strip()
        cas_info[key] = value
    return cas_info

def site_crawler():
    cas_boss()

def products_catalog_crawler():
    main_page = 'http://www.chemnet.com/Global/Products/'
    catalog_pattern = re.compile(r'<a\s+href="(/Global/Products/[^"]+?)"\s+class="blue">(.*?)</a>', re.S)
    resp = _http_call(main_page)
    datas = catalog_pattern.findall(resp.text)
    for url, name in datas:
        print url, name


def products_crawler():
    pass

def suppliers_crawler():
    pass

def buy_cralwer():
    pass

def sell_crawler():
    pass

if __name__ == '__main__':
    site_crawler()


