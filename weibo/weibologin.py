#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import re
import json
import requests
import traceback

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
    'pwencode': 'encrypt',
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
    data = requests.get(url).content;
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
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.1)'
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
#    postdata_params = urllib.urlencode(postdata)
#    print postdata_params
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/12.04 Chromium/18.0.1025.168 Chrome/18.0.1025.168 Safari/535.19'}
    result = session.post(
        url=url,
        data=postdata,
        headers=headers
    )
    text = result.content
    text = result.content.decode("GBK")
    print text.encode("UTF-8")
    p = re.compile('location\.replace\(\'(.*?)\'\)')

    try:
        login_url = p.search(text).group(1)
        session.get(login_url)
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


#hzwangpin@sina.com wx871125
#users = [["hzwangpin@sina.com", "wx871125"]]
#for username, password in users:
#    print username, password
#    login(username, password)
#    weibo_content = session.get('http://e.weibo.com/1739959962/ywW0JyWsO?ref=http%3A%2F%2Fweibo.com%2Fxceman%3Fwvr%3D3.6%26lf%3Dreg')
#    pattern = re.compile(r'mid=(\d+)&name=[^&]+&uid=(\d+)')
#    weibo_match = pattern.search(weibo_content.content)
#    print weibo_match.group(1)
if __name__ == '__main__':
    login('xeoncode@gmail.com', '5845211314')