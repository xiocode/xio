#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback

__author__ = 'Tony.Shao'

import re

re.compile(r'')


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar.strip():
        uchar = uchar.decode('utf-8')
        for char in uchar:
            if u'\u4e00' <= char <= u'\u9fa5':
                return True
        return False

bangs = ['FS', 'HZP', 'MY', 'SM']
for bang in bangs:
    with open('top_bang_TR_%s.txt' % bang, 'r') as FILE:
        with open('top_bang_TR_%s_new.txt' % bang, 'a') as NEW_FILE:
            for line in FILE:
                top_bang = line.strip()
                if is_chinese(top_bang) and ' ' not in top_bang:
                    print top_bang
                    NEW_FILE.write(top_bang + '\n')
