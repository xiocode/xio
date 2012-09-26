#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'
from peewee import *

db = MySQLDatabase('xio', host='localhost', user='root', passwd='299792458')

class BaseModel(Model):
    class Meta:
        database = db

class tb_category_info(BaseModel):
    cid = CharField()
    pid = CharField()
    name = CharField()
    url = CharField()

class tb_company_info(BaseModel):
    cid = CharField()
    company_id = IntegerField()
    company_name = CharField()
    company_description = TextField()
    business_type = CharField()
    industry_focus = TextField()
    services_products = TextField()
    year_established = CharField()
    employees = CharField()
    annual_revenue = CharField()
    geographic_markets = CharField()
    brand_name = CharField()
    certificates = CharField()
    contact_person = CharField()
    company_address = CharField()
    city = CharField()
    province = CharField()
    country = CharField()
    zip = CharField()
    phone_number = CharField()
    fax_number = CharField()
    homepage = CharField()


class tb_product_info(BaseModel):
    cid = CharField()
    company_id = IntegerField()
    product_id = IntegerField()
    product_name = CharField()
    description = TextField()

class tb_sell_info(BaseModel):
    cid = CharField()
    company_id = IntegerField()
    sell_id = IntegerField()
    product_name = CharField()
    description = TextField()