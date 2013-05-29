#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import re
import json
from urlparse import urlparse, parse_qs
import requests
import traceback
from requests.compat import cookielib
import time

APP_KEY = "xxxxx"
APP_SECRET = 'xxxxx'
CALLBACK_URL = 'http://2.xweiboproxy.sinaapp.com/callback.php'
RSA_SERVER_URL = 'http://localhost:8888/encrypt?password=%s'
session = requests.session()
session.timeout = 10

postdata = {
    'entry': 'weibo',
    'gateway': '1',
    'from': '',
    'savestate': '7',
    'userticket': '1',
    'ssosimplelogin': '1',
    'vsnf': '1',
    'su': '',
    'service': 'miniblog',
    'servertime': '',
    'nonce': '',
    'pwencode': 'rsa2',
    'rsakv': '',
    'sp': '',
    'encoding': 'UTF-8',
    'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
    'returntype': 'META'
}


def __get_servertime():
    '''
            获取服务器时间和nonce随机数
    '''
    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=dW5kZWZpbmVk&rsakt=mod&client=ssologin.js(v1.4.1)&_=1344575024059'
    data = requests.get(url).text;
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
    return resp.content


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
        servertime, nonce, rsakv = __get_servertime()
    except Exception, e:
        print e
        return None
    global postdata
    postdata['servertime'] = servertime
    postdata['nonce'] = nonce
    postdata['su'] = __get_user(username)
    postdata['sp'] = __get_pwd(pwd)
    postdata['rsakv'] = rsakv
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/12.04 Chromium/18.0.1025.168 Chrome/18.0.1025.168 Safari/535.19'}

    result = session.post(
        url=url,
        data=postdata,
        headers=headers,
    )
    text = result.text
    p = re.compile('location\.replace\(\"(.*?)\"\)')

    try:
        COOKIEJAR_CLASS = cookielib.LWPCookieJar
        cookiejar = COOKIEJAR_CLASS('weibo_cookies')
        login_url = p.search(text).group(1)
        session.get(login_url, cookies=cookiejar)
        cookiejar.save()
        print 'Login Success！'
    except Exception:
        print traceback.format_exc()
        return None

def getToken():
    authorize_url = "https://api.weibo.com/oauth2/authorize?client_id=%s&redirect_uri=%s&response_type=token" % (
        APP_KEY, CALLBACK_URL)
    response = session.get(authorize_url, allow_redirects=False)
    callback_url = response.headers.get('location')
    qs = parse_qs(urlparse(callback_url).fragment)
    token = qs.get('access_token')
    expires_in = qs.get('expires_in')
    if token:
        # expires等于当前时间加上有效期，单位为秒
        expires = int(expires_in[0]) + int(time.time())
        return token[0], expires

class WeiboError(StandardError):
    def __init__(self, error_code, error):
        self.error_code = error_code
        self.error = error
        StandardError.__init__(self, error)

    def __str__(self):
        return 'TokenGeneratorError: ErrorCode: %s, ErrorContent: %s' % (self.error_code, self.error)

if __name__ == '__main__':
    login('xxxxx', 'xxxxx')