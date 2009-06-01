#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class UserDbMaster(BaseModel):
  name = db.StringProperty(required=True)
  yaml_data = db.TextProperty()

class UserDb(BaseModel):
  user  = db.UserProperty(required=True)
  name  = db.StringProperty(default=u'新規データベース')
  service_type = db.StringProperty(default='p') # 'c': 問い合わせ
