#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

import requests
import re
from gevent.pool import Group
from gevent.queue import JoinableQueue
import gevent
import traceback
from tables import tb_20130112_supplies_info, tb_20130112_category_info
from database import tb_20130112_products_info, db_session
from multiprocessing import Process

proxies = {
    'http': '127.0.0.1:8087'
}

PROXY_IP = '127.0.0.1'

headers = {
    'X-Forwarded-For': '%s, 127.0.0.1, 192.168.0.1' % PROXY_IP,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.43 Safari/536.11'
}

session = requests.session()
session.headers = headers

def _http_call(url):
    try:
        return session.get(url=url)
    except Exception:
        print traceback.format_exc()
        return None

suppliers_group = Group()
suppliers_queue = JoinableQueue()

next_page_pattern = re.compile(r'<a\s+href=\'([^\']+?)\'>Next &gt; </a>')
suppliers_outer_pattern = re.compile(
    r'<li\s+id="li_([^"]+?)">.*?<a\s+href="([^"]+?)"\s+target="_blank">.*?</a>.*?<p><span>Country/Region:</span><em><img\s+src="[^"]+?">&nbsp;([^<]+?)</em></p>', re.S)
suppliers_inner_pattern = re.compile(r'<p\s+class="lh22\s+pd_r15">(.*?)</p>.*?<table\s+border="0"\s+cellspacing="3"\s+cellpadding="0"\s+width="100%"\s+class="tab\s+mt10\s+mb20">(.*?)</table>.*?<div\s+class="ID">([^<]+?)<span>.*?<a\s+href="mailto:([^"]+?)">.*?<p>Tel:(.*?)<br\s+/>\s+Fax:(.*?)<br\s+/>', re.S)
suppliers_base_url = 'http://www.guidechem.com/suppliers/list_letter-%s.html'
cat_url = 'http://www.guidechem.com/product/'
cat_base_url = 'http://www.guidechem.com/product/list_catid-%s.html'
cat_pattern = re.compile(r'<li><a href="list_catid-(\d+).html".*?>([^<]+?)</a>')
products_outer_pattern = re.compile(r'<li\s+id="li_([^"]+?)"\s+>.*?<a\s+href="([^"]+?)"\s+target="_blank"\s+title="([^"]+?)">.*?</a>\s+(?:<a\s+href="[^"]+?"\s+target="_blank"\s+class="cas">\(\s+CAS:([^\s]+?)\s+\)</a>)?\s+</h3>.*?<a\s+href="http://([^\.]+?).guidechem.com/"', re.S)
products_inner_pattern = re.compile(r'<div\s+class="product_detail"\s+id="product_detail">(.*?)</div>\s+<div style="display:none;"', re.S)
BASE_URL = 'http://www.guidechem.com'
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
suppliers_inner_packet_pattern = re.compile(r'<td\s+width="22%"\s+height="34">([^<]+?)</td>\s+<td\s+width="78%">([^<]+?)</td>', re.S)


def suppliers_boss():
    for i in xrange(0, 26):
        url = suppliers_base_url % LETTERS[i]
        print url
        suppliers_queue.put(url)

    for x in xrange(10):
        suppliers_group.spawn(suppliers_worker)

    suppliers_group.join()


def suppliers_worker():
    while not suppliers_queue.empty():
        try:
            url = suppliers_queue.get()
            print url
            outer_resp = _http_call(url)
            outer_text = outer_resp.text
            next_page_url = next_page_pattern.findall(outer_text)
            if next_page_url:
                url = BASE_URL + next_page_url[0]
                print 'Next: ' + url
                suppliers_queue.put(url)
            suppliers_outer_parser(outer_text)
        except Exception:
            print traceback.format_exc()
        finally:
            suppliers_queue.task_done()
            gevent.sleep(0.0)


def suppliers_outer_parser(outer_text):
#    print outer_text
    suppliers_infos = {}
    outer_datas = suppliers_outer_pattern.findall(outer_text)
    for supplier_id, url, region in outer_datas:
        try:
            resp = _http_call(url + "cominfo.html")
            suppliers_infos['supplier_id'] = supplier_id
            suppliers_infos['region'] = region
            suppliers_infos.update(suppliers_inner_parser(resp.text))
            suppliers_info = tb_20130112_supplies_info(**suppliers_infos)
            print url
            suppliers_info.save()
            print '已经抓取 ' + supplier_id
        except Exception as e:
            print traceback.format_exc()

def suppliers_inner_parser(inner_text):
    supplier_info = {}
    try:
        inner_datas = suppliers_inner_pattern.findall(inner_text)[0]
        description = inner_datas[0].strip()
        supplier_info['description'] = description
        inner_packet = inner_datas[1].strip()
        contact_name = inner_datas[2].strip()
        supplier_info['contact_name'] = contact_name
        contact_email = inner_datas[3].strip()
        supplier_info['contact_email'] = contact_email
        contact_telephone = inner_datas[4].strip()
        supplier_info['contact_telephone'] = contact_telephone
        contact_fax = inner_datas[5].strip()
        supplier_info['contact_fax'] = contact_fax
        inner_packet_datas = suppliers_inner_packet_pattern.findall(inner_packet)
        for key, value  in inner_packet_datas:
            key = format_key(key)
            value = value.strip()
            supplier_info[key] = value
    except IndexError as e:
        print inner_text

    return supplier_info

#########################################

def cat_parser():
#    print outer_text
    outer_resp = _http_call(cat_url)
    outer_text = outer_resp.text
    cat_infos = {}
    outer_datas = cat_pattern.findall(outer_text)
    for cat_id, cat_name in outer_datas:
        try:
            cat_infos['cat_id'] = cat_id
            cat_infos['cat_name'] = cat_name
            cat_info = tb_20130112_category_info(**cat_infos)
            print cat_id
            cat_info.save()
        except Exception as e:
            print traceback.format_exc()

############################################
from multiprocessing import Queue
products_queue = Queue()
def products_boss():
    results = tb_20130112_category_info.select().execute()
    for result in results:
        url = cat_base_url % result.cat_id
        products_queue.put(url)

    for x in xrange(20):
#        suppliers_group.spawn(products_worker)
        process = Process(target=products_worker)
        process.start()


def products_worker():
    while not products_queue.empty():
        try:
            url = products_queue.get()
            print url
            outer_resp = _http_call(url)
            outer_text = outer_resp.text
            next_page_url = next_page_pattern.findall(outer_text)
            if next_page_url:
                url = BASE_URL + next_page_url[0]
                print 'Next: ' + url
                products_queue.put(url)
            products_outer_parser(outer_text)
        except Exception:
            print traceback.format_exc()


def products_outer_parser(outer_text):
#    print outer_text

    outer_datas = products_outer_pattern.findall(outer_text)
    for products_id, url, name, cas_id, suppliers_url_id in outer_datas:
        try:
            products_infos = {}
            resp = _http_call(BASE_URL + url)
            products_infos['products_id'] = products_id
            products_infos['name'] = name
            products_infos['cas_id'] = cas_id
            products_infos['suppliers_url_id'] = suppliers_url_id
            products_infos.update(products_inner_parser(resp.text))
            products_info = tb_20130112_products_info(**products_infos)
            print url
            db_session.add(products_info)
            db_session.commit()
            print '已经抓取 ' + products_id
        except Exception as e:
            print traceback.format_exc()
        finally:
            db_session.remove()

def products_inner_parser(inner_text):
    products_info = {}
    try:
        inner_datas = products_inner_pattern.findall(inner_text)
        description = inner_datas[0].strip()
        products_info['detail'] = description
    except IndexError as e:
        print inner_text

    return products_info



def strip_tags(html):
    return re.sub('<[^<]+?>', ' ', html)


def format_key(key):
    return '_'.join(key.lower().strip().split(' '))



def site_crawler():
    suppliers_boss()


if __name__ == '__main__':
    products_boss()


