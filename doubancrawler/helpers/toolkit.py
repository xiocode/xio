#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

from doubancrawler.libs.douban import DoubanClient

def get_douban_client():
    API_KEY = '0a6479e7b9ccf53e1f2d6db72d66dfba'
    API_SECRET = '11d9e8ce36af8227'
    CALLBACK_URI = '127.0.0.1'
    SCOPE = 'douban_basic_common,community_basic_user'
    client = DoubanClient(API_KEY, API_SECRET, CALLBACK_URI, SCOPE)
    return client