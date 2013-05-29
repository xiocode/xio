#!/usr/bin/env python
# -*- coding: utf-8 -*-
from doubancrawler.helpers.toolkit import get_douban_client

__author__ = 'Tony.Shao'


douban_client = get_douban_client()
print douban_client.authorize_url
code = raw_input('Enter the verification code:')
douban_client.auth_with_code(code)
print douban_client.user.me