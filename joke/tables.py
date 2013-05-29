#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'
from peewee import *

#db = MySQLDatabase('xio', host='localhost', user='root', passwd='root', threadlocals=True)
db = MySQLDatabase('xio', host='localhost', user='root', passwd='299792458', threadlocals=True)

class BaseModel(Model):
    class Meta:
        database = db

class tb_joke(BaseModel):
    id = PrimaryKeyField()
    title = CharField()
    content = TextField()


