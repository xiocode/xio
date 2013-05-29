#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import re
import json
import requests
import traceback
import time
import ujson

RSA_SERVER_URL = 'http://localhost:8888/rsa?password=%s'
session = requests.session()
session.timeout = 10

postdata = {
    'entry': 'qing',
    'gateway': '1',
    'from': '',
    'savestate': '30',
    'userticket': '1',
    'su': '',
    'service': 'miniblog',
    'servertime': '',
    'nonce': '',
    'pwencode': 'rsa',
    'rsakv': '',
    'sp': '',
    'encoding': 'UTF-8',
    'callback': 'sinaSSOController.loginCallBack',
    'client': 'ssologin.js(v1.4.2)',
    'cdult': '2',
    'prelt': '114',
    'domain': 'weibo.com',
    'returntype': 'TEXT',
    '_': ''
}


def __get_server_params():
    '''
            获取服务器时间和nonce随机数
    '''
    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=qing&callback=sinaSSOController.preloginCallBack&su=eGVvbmNvZGUlNDBnbWFpbC5jb20%3D&rsakt=mod&client=ssologin.js(v1.4.2)&_=1347847946672'
    data = session.get(url).text;
    p = re.compile('\((.*)\)')
    try:
        json_data = p.search(data).group(1)
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        rsakv = data['rsakv']
        return servertime, nonce, rsakv
    except:
        print 'Get severtime error!'
        return None


def __get_pwd(pwd):
    '''
    RSA加密
    '''
    global session
    resp = session.get(RSA_SERVER_URL % pwd)
    return resp.text


def __get_user(username):
    '''
    username 经过了BASE64 计算
    '''
    username_ = requests.compat.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username


def login(username, pwd):
    global session
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)'
    try:
        servertime, nonce, rsakv = __get_server_params()
    except Exception, e:
        print e
        return None
    global postdata
    postdata['servertime'] = servertime
    postdata['nonce'] = nonce
    postdata['su'] = __get_user(username)
    postdata['sp'] = __get_pwd(pwd)
    postdata['rsakv'] = rsakv
    postdata['_'] = int(time.time())

    #    return

    #http://login.sina.com.cn/sso/login.php?entry=qing&gateway=1&from=&savestate=30&useticket=1&su=eGVvbmNvZGUlNDBnbWFpbC5jb20%3D&service=miniblog&servertime=1347873165&nonce=UF5RQM&pwencode=rsa2&rsakv=1330428213&sp=4a92a5ab9ffa0a2ac356002353ac13dc107ea7c6d26776b9c13162d87a0a4c493bd1dfd35c17768a86f7d255b0850eb4cea57e6a053d3d22f60e397c03e3813fc9bee42be37917b4cceda00562353866956cc7f3ebf03e369efed3947b578c73e64d62828c60827eee150f277e190b185c70f6ae248ad318c3d09239ef093457&encoding=UTF-8&callback=sinaSSOController.loginCallBack&cdult=2&domain=weibo.com&prelt=76&returntype=TEXT&client=ssologin.js(v1.4.2)&_=1347873165203
    #http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)&nonce=HGAZBO&domain=weibo.com&savestate=30&from=&service=miniblog&encoding=UTF-8&sp=d8e60ed9c1fdbdcc70d93c00d70cec806bda110d2d348e9ec6d2de13e66bae8ec8ac4b1bd9a52dc7b272f0750aa7a41906507123c8669e3b51f5a3ccc7f132c8594d452f8ac9a7e0b276d54ac76f94c6fe745aba379449913513d9613af2beff9258f0d4322c96abb89ee2920836fdcc130e0950450540c07ff6d6dc412a6ed2&servertime=1347873059&su=eGVvbmNvZGUlNDBnbWFpbC5jb20%3D&rsakv=1330428213&callback=sinaSSOController.loginCallBack&prelt=114&client=ssologin.js%28v1.4.2%29&userticket=1&returntype=TEXT&entry=qing&cdult=2&gateway=1&_=1347873059&pwencode=rsa2

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/12.04 Chromium/18.0.1025.168 Chrome/18.0.1025.168 Safari/535.19',
        'Cookie': 'U_TRS1=000000fa.79a85135.505694b7.812ddc43; SINAGLOBAL=000000fa.8f4b100f.505694cb.88b2a1ab; Apache=000000fa.61c762c5.5056e946.ec055441',
        'Referer': 'http://qing.weibo.com/'}
    result = session.get(
        url=url,
        params=postdata,
        headers=headers
    )
#    print result.url
    text = result.text
#    print text
    #    p = re.compile(r'\"ticket\":\(\"(.*?)\"\)')
    p = re.compile(r'sinaSSOController.loginCallBack\((.*?)\)')
    try:
        match = p.search(text).group(1);
        match = ujson.decode(match)
        login_ticket = match['ticket']
        login_url = 'http://weibo.com/sso/login.php?callback=sinaSSOController.customLoginCallBack&ticket=' + login_ticket + '&ssosavestate=' + str(
            int(time.time() / 1000)) + '&client=ssologin.js(v1.4.2)&_=' + str(int(time.time()))
        resp = session.get(login_url)
        print resp.text
#        print resp.text
#        resp = session.get('http://weibo.com')
#        print resp.text
    except Exception:
        print traceback.format_exc()
        return None


class WeiboError(StandardError):
    def __init__(self, error_code, error):
        self.error_code = error_code
        self.error = error
        StandardError.__init__(self, error)

    def __str__(self):
        return 'TokenGeneratorError: ErrorCode: %s, ErrorContent: %s' % (self.error_code, self.error)


if __name__ == '__main__':
    login('xeoncode@gmail.com', '5845211314')
