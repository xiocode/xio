#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

from weibo.tencent.app.helpers.tencent_weibo import APIClient


weibo = APIClient()

#https://open.t.qq.com/cgi-bin/oauth2/authorize?redirect_uri=http%3A//127.0.0.1%3A8070/weibo/callback&response_type=code&client_id=379bdd7227c940c1ad42df6f38bc9ed2
#token = 151bc93f50c1915a90e5fe798d2a32f9
#expires = 1349247331

weibo.set_access_token('151bc93f50c1915a90e5fe798d2a32f9', '9803EA6844D2275E3540CEE8D3AB09AF', '1349247831')
timeline = weibo.get.statuses__public_timeline()
print timeline