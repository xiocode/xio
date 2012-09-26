#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tony.Shao'
from peewee import *

db = MySQLDatabase('xio', host='localhost', user='root', passwd='299792458')

class BaseModel(Model):
    class Meta:
        database = db

class tb_20120924_cas_info(BaseModel):
    id = PrimaryKeyField()
    cas_id = CharField()
    product_name = TextField()
    synonyms = TextField()
    molecular_formula = CharField()
    molecular_weight = CharField()
    inchi = CharField()
    cas_registry_number = TextField()
    molecular_structure = CharField()
    einecs = CharField()
    density = CharField()
    boiling_point = CharField()
    refractive_index = CharField()
    melting_point = CharField()
    flash_point = CharField()
    water_solubility = CharField()
    vapour_pressur = CharField()
    hazard_symbols = CharField()
    risk_codes = CharField()
    safety_description = CharField()
    url = TextField()