#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

'''
'''
class Prefecture(BaseModel):
  code = db.StringProperty(required=True) # ISO 3166-2:JP <strike>JIS X0401 全国地方公共団体コード</strike>
  name = db.StringProperty(required=True)
