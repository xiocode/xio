#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'
import requests
import re
from tables import tb_category_info, tb_company_info, tb_product_info,tb_sell_info
import traceback
from django.utils.html import strip_tags, clean_html

proxies = {
    'http': '127.0.0.1:8087'
}

headers = {
    'Cookie': 'ASP.NET_SessionId=pevb2vi2alibdb45wog1k445',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.43 Safari/536.11'
    ,
    'Host': 'www.b2bchem.net'
}

session = requests.session(headers=headers)

'''
<A\s+href="http://www.b2bchem.net/company/cat([^"]+?)"\s+title="([^"]+?)">
<table\s+width="90%">(.*?)</table>
<a\s+href="http://www.b2bchem.net/company/([^"]+?)"\s+title="([^"]+?)">
'''

p_category_pattern = re.compile(r'<A\s+href="http://www.b2bchem.net/company/([^"]+?)"\s+title="([^"]+?)">')
c_category_pattern_chunk = re.compile(r'<table\s+width="90%">(.*?)</table>', re.S)
c_category_pattern = re.compile(r'<a\s+href="http://www.b2bchem.net/company/([^"]+?)"\s+title="([^"]+?)">')

next_pattern = re.compile(r'<A\s+href\s+=\s+"([^"]+?)">Next</A>')

company_url_pattern = re.compile(r'<A\s+href="(http://www.b2bchem.net/showroom/[^"]+?)">')
company_id_pattern = re.compile(r'http://www.b2bchem.net/showroom/(\d+)/.*?', re.S)
company_info_pattern = re.compile(
    r'<TD\s+align="center"\s+height="30"\s+class="font16">([^<]+?)</STRONG></TD>.*?<TD\s+align="left"><br>([^<]+?)</TD>.*?\s+<TABLE\s+cellSpacing="0"\s+cellPadding="0"\s+width="95%"\s+align="center"\s+border="0">(.*?)</TABLE>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>.*?</td>\s+<td.*?>(.*?)</td>'
    , re.S)

company_profile_pattern = re.compile(r'<TD\s+align="left"\s+width="25%">(.*?)</TD>\s+<TD\s+align="left" width="25%">(.*?)</TD>')

product_url_pattern = re.compile(r'<A\s+href="(http://www.b2bchem.net/showroom/product/[^"]+?).*?">')
product_id_pattern = re.compile(r'http://www.b2bchem.net/showroom/product/(\d+)/(.*?)\.aspx', re.S)
product_description_pattern =  re.compile(r'<TR\s+align="center">(.*?)<table width="100%"', re.S)

sell_url_pattern = re.compile(r'<A\s+href="(http://www.b2bchem.net/showroom/trade/[^"]+?)".*?>')
sell_id_pattern = re.compile(r'http://www.b2bchem.net/showroom/trade/(\d+)/(.*?)\.aspx', re.S)
sell_description_pattern = re.compile(r'<TR\s+align="center">(.*?)<table width="100%"', re.S)

COMPANY_BASE_URL = 'http://www.b2bchem.net/company/'
PRODUCTS_BASE_URL = 'http://www.b2bchem.net/product/'
SELL_BASE_URL = 'http://www.b2bchem.net/sell/'

def _http_call(url):
    resp = session.get(url, allow_redirects=False)
    if resp.status_code == 200:
        text = resp.text
        return text
    else:
        print '网页返回错误！'


def category_crawler():
    content = _http_call('http://www.b2bchem.net/company.aspx')
    content = content.replace('&amp;', ' ').strip('\r').strip('\n').strip('\t')
    category_groups = c_category_pattern_chunk.findall(content)
    #    for category in category_groups[0]:
    category = category_groups[0][5]
    categorys = c_category_pattern.findall(category)
    print categorys
    for category in categorys:
        id, url = category[0].split('/')
        name = category[1]
        data = {'cid': id, 'pid': 'cat6', 'name': name, 'url': url}
        category = tb_category_info(**data)
        category.save()
        print id, url, name


def company_crawler():
    results = tb_category_info.select().where(pid__ne = '0').execute()
    for result in results:
        url_path = COMPANY_BASE_URL + result.cid + '/' + result.url
        while url_path:
            print url_path
            resp = session.get(url_path)
            url_path = next_pattern.findall(resp.text)
            if url_path:
                url_path = url_path[0]
            urls = company_url_pattern.findall(resp.text)
            for url in urls:
                try:
                    company_info = {}
                    print url
                    company_id = company_id_pattern.findall(url)[0]
                    company_info['cid'] = result.cid
                    company_info['company_id'] = company_id
                    resp = session.get(url)
                    groups = company_info_pattern.findall(resp.text)
                    company_info['company_name'] = groups[0][0]
                    company_info['company_description'] = groups[0][1].strip()

                    company_profile_block = groups[0][2]
                    matchs = company_profile_pattern.findall(company_profile_block)
                    for match in matchs:
                        if 'Business' in match[0]:
                            company_info['business_type'] = match[1]
                        elif 'Industry' in match[0]:
                            company_info['industry_focus'] = match[1]
                        elif 'Services' in match[0]:
                            company_info['services_products'] = match[1]
                        elif 'Year' in match[0]:
                            company_info['year_established'] = match[1]
                        elif 'Employees' in match[0]:
                            company_info['employees'] = match[1]
                        elif 'Annual' in match[0]:
                            company_info['annual_revenue'] = match[1]
                        elif 'Geographic' in match[0]:
                            company_info['geographic_markets'] = match[1]
                        elif 'Certificates' in match[0]:
                            company_info['certificates'] = match[1]
                        elif 'Brand' in match[0]:
                            company_info['brand_name'] = match[1]
                        else:
                            print match

                    company_info['contact_person'] = groups[0][3]
                    company_info['company_address'] = groups[0][4]
                    company_info['city'] = groups[0][5]
                    company_info['province'] = groups[0][6]
                    company_info['country'] = groups[0][7]
                    company_info['zip'] = groups[0][8]
                    company_info['phone_number'] = groups[0][9]
                    company_info['fax_number'] = groups[0][10]
                    company_info['homepage'] = groups[0][11]
                    print company_info
                    company_info_db = tb_company_info(**company_info)
                    company_info_db.save()
                except Exception as e:
                    print traceback.format_exc()
                    if 'list index out of range' in e.message:
                        with open('error.txt', 'a') as FILE:
                            FILE.write(url + '\n')
                    print '出错'

def products_info():
    results = tb_category_info.select().where(pid__ne = '0').execute()
    for result in results:
        url_path = PRODUCTS_BASE_URL + result.cid + '/' + result.url
        while url_path:
            print url_path
            resp = session.get(url_path)
            url_path = next_pattern.findall(resp.text)
            if url_path:
                url_path = url_path[0]
                urls = product_url_pattern.findall(resp.text)
                for url in urls:
                    try:
                        product_info = {}
                        print url
                        product_id, product_name = product_id_pattern.findall(url)[0]
                        resp = session.get(url)
    #                    groups = company_info_pattern.findall(resp.text)
                        company_id = company_id_pattern.findall(resp.text)[0]
                        product_description = product_description_pattern.findall(resp.text)[0].strip()
                        product_info['cid'] = result.cid
                        product_info['product_id'] = product_id
                        product_info['company_id'] = company_id
                        product_info['product_name'] = product_name.strip()
                        product_info['description'] = clean_html(product_description)
                        print product_info
                        product_info_db = tb_product_info(**product_info)
                        product_info_db.save()
                    except Exception:
                        print traceback.format_exc()
                        with open('product_error.txt', 'a') as FILE:
                            FILE.write(url + '\n')
                        print '出错'


def offer_to_sell():
    results = tb_category_info.select().where(pid__ne = '0').execute()
    for result in results:
        url_path = SELL_BASE_URL + result.cid + '/' + result.url
        while url_path:
            print url_path
            resp = session.get(url_path)
            url_path = next_pattern.findall(resp.text)
            if url_path:
                url_path = url_path[0]
                urls = sell_url_pattern.findall(resp.text)
                for url in urls:
                    try:
                        sell_info = {}
                        print url
                        sell_id, product_name = sell_id_pattern.findall(url)[0]
                        resp = session.get(url)
                        #                    groups = company_info_pattern.findall(resp.text)
                        company_id = company_id_pattern.findall(resp.text)[0]
                        product_description = sell_description_pattern.findall(resp.text)[0].strip()
                        sell_info['cid'] = result.cid
                        sell_info['sell_id'] = sell_id
                        sell_info['company_id'] = company_id
                        sell_info['product_name'] = product_name.strip()
                        sell_info['description'] = strip_tags(product_description).strip()
                        print sell_info
                        sell_info_db = tb_sell_info(**sell_info)
                        sell_info_db.save()
                    except Exception:
                        print traceback.format_exc()
                        with open('sell_error.txt', 'a') as FILE:
                            FILE.write(url + '\n')
                        print '出错'


if __name__ == '__main__':
    offer_to_sell()