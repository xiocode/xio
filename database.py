#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, DATETIME, TEXT, ENUM, DECIMAL, TIMESTAMP
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import when

__author__ = 'Tony.Shao'
DB_CONNECT_STRING = 'mysql+mysqldb://root:299792458@localhost/xio?charset=utf8'
def createEngine():
    engine = create_engine(DB_CONNECT_STRING, convert_unicode=True, pool_recycle=3600, echo=False)
    return engine

engine = createEngine()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Model = declarative_base(name='Model')
Model.query = db_session.query_property()

class tb_20130112_products_info(Model):
    __tablename__ = 'tb_20130112_products_info'

    id = Column(INTEGER, primary_key=True)
    products_id = Column(INTEGER)
    name = Column(VARCHAR(255))
    cas_id = Column(VARCHAR(255))
    suppliers_url_id = Column(VARCHAR(255))
    detail = Column(TEXT)

