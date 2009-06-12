#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

import yaml

class UserDb(BaseModel):
  user  = db.UserProperty(required=True)
  name  = db.StringProperty(default=u'新規データベース')
  service_type = db.StringProperty(default='p') # 'c': 問い合わせ

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
