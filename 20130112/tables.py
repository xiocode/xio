#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'
from peewee import *

#db = MySQLDatabase('xio', host='localhost', user='root', passwd='root', threadlocals=True)
db = MySQLDatabase('xio', host='localhost', user='root', passwd='299792458', threadlocals=True, autocommit=True)

class BaseModel(Model):
    class Meta:
        database = db

class tb_20130112_supplies_info(BaseModel):
    id = PrimaryKeyField()
    supplier_id = CharField()
    name = CharField()
    region = CharField()
    category = CharField()
    country_region = CharField()
    trade_category = CharField()
    registered_time = CharField()
    registered_capital = CharField()
    legal_representative = CharField()
    employees = CharField()
    address = CharField()
    website = CharField()
    product_service = CharField()
    description = TextField()
    contact_name = CharField()
    contact_telephone = CharField()
    contact_fax = CharField()
    contact_email = CharField()
    contact_address = CharField()
    contact_square = CharField()

class tb_20130112_category_info(BaseModel):
    id = PrimaryKeyField()
    cat_id = CharField()
    cat_name = CharField()

class tb_20130112_products_info(BaseModel):
    id = PrimaryKeyField()
    products_id = IntegerField()
    name = CharField()
    cas_id = CharField()
    suppliers_url_id = CharField()
    detail = TextField()


