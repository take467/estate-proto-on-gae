#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class UserDb(BaseModel):
  user  = db.UserProperty(required=True)
  name  = db.StringProperty(default=u'新規データベース')
