#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.user_db import UserDb
import yaml

class UserView(BaseModel):
  user_db_id     = db.ReferenceProperty(UserDb)
  name   = db.StringProperty(default=u'新規ビュー')
  config = db.TextProperty()

  def getProperty(self,key):
    prop =  yaml.load(self.config)
    if key in prop:
      return prop.get(key) 
    else:
      return None

  def setProperty(self,key,val):
    prop =  yaml.load(self.config)
    prop[key] = val
    self.config = yaml.dump(prop)
