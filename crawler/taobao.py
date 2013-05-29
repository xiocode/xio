#!/usr/bin python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

import requests
import time
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

session = requests.session()

urls = ["TR_FS", "TR_HZP", "TR_MY", "TR_SM"]

sub_bang_query = "http://top.taobao.com/interface2.php?cat=%s&jsv=nav_%s"
top_bang_base_url = "http://top.taobao.com/level3.php?%s&level3=&show=brand&up=false&ad_id=&am_id=&cm_id=&pm_id="
top_bangs_list = []
sub_bangs_pattern = re.compile(r'(cat=.*?)\\"', re.S)
top_bangs_pattern = re.compile(r'</script></map>\s+<a\s+href=.*?>([^>]+?)</a>', re.S)
top_bangs_next_page_pattern = re.compile(r'<a\s+href="([^"]+?)"\s+class="page-next"\s+target="_self">')
for url in urls:
    with open('top_bang_%s.txt' % url, 'a') as FILE:
        print url
        resp = session.get(sub_bang_query % (url, int(time.time())))
        body = resp.text
        # print content
        sub_bangs = sub_bangs_pattern.findall(body)
        if sub_bangs:
            for sub_bang in sub_bangs:
                print sub_bang
                top_bang_url = top_bang_base_url % sub_bang
                while True:
                    top_bang_resp = session.get(top_bang_url)
                    top_bang_body = top_bang_resp.text
                    top_bang_next_page = top_bangs_next_page_pattern.findall(top_bang_body)
                    if not top_bang_next_page:
                        break
                    top_bang_url = top_bang_next_page[0]
                    top_bangs = top_bangs_pattern.findall(top_bang_body)
                    for top_bang in top_bangs:
                        print top_bang
                        top_bang = top_bang.split('/')
                        for bang in top_bang:
                            if bang not in top_bangs_list:
                                FILE.write(bang + '\n')
                                top_bangs_list.append(bang)
            FILE.write('\n')


