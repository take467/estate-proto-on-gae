#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.user_db import UserDb

class UserView(BaseModel):
  user_db_id     = db.ReferenceProperty(UserDb)
  name   = db.StringProperty(default=u'新規ビュー')
  config = db.TextProperty()
  pass
