#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

from weibo.helpers import utils
from weibo.tencent.app.helpers.tencent_weibo import APIClient

class authorize_callback():
    def GET(self):
        params = utils.get_url_params()
        code = params.get('code')
        openid = params.get('openid')
        openkey = params.get('openkey')
        print code
        client = APIClient()
        resp = client.request_access_token(code)
        resp.openid = openid
        resp.openkey = openkey
        return resp
