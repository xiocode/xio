#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'

import logging

def getLogger(logger_name=""):
    #create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    #create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    #create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(module)s - %(lineno)d - %(levelname)s - %(message)s")
    #add formatter to ch
    ch.setFormatter(formatter)
    #add ch to logger
    logger.addHandler(ch)
    return  logger
