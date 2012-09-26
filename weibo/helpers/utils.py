#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'
__version__ = '0.0.1'

import web
import urlparse
import  types
import traceback
import logging
from hashlib import md5
import time

ENCRYPTION_KEY = 'abcdefghijklmnopqrstuvwxyz1234567890'

def getLogger(logger_name=""):
    #create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    #create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    #create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(module)s - %(pathname)s - %(lineno)d - %(levelname)s - %(message)s")
    #add formatter to ch
    ch.setFormatter(formatter)
    #add ch to logger
    logger.addHandler(ch)
    return  logger


def get_all_functions(module):
    functions = {}
    for f in [module.__dict__.get(a) for a in dir(module)
              if isinstance(module.__dict__.get(a), types.FunctionType)]:
        functions[f.__name__] = f
    return functions


def get_url_params():
    try:
        parsed_url = urlparse.urlparse(web.ctx.fullpath)
        query_dict = dict(urlparse.parse_qsl(parsed_url.query))
        return query_dict
    except Exception:
        print traceback.format_exc()
        return None


def make_unique_md5(source=None):
    if not source:
        source = time.ctime()
    return md5(source + ENCRYPTION_KEY).hexdigest()


if __name__ == '__main__':
    rs = make_unique_md5()
    print rs
    print len(rs)