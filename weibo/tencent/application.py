#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'
import web

urls = (
    '/weibo/callback', 'weibo.tencent.app.controllers.actions.authorize_callback' #认证
    )

if __name__ == "__main__":
#web.config.debug = False
    app = web.application(urls, globals())
    app.run()
