#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.user_db import UserDb
from model.profile import *
from model.inquiry import *
import yaml
import copy

class UserView(BaseModel):
  user_db_id     = db.ReferenceProperty(UserDb)
  name   = db.StringProperty(default=u'新規ビュー')
  config = db.TextProperty()

  def user_db(self):
    return self.user_db_id

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

  @classmethod
  def newInstance(cls,udb,):
    # ついでにビューもつくってしまう
    cols = None
    if udb.service_type == 'c':
      # 問い合わせフォーム専用ビュー
      cols = udb.getProperty('form_config')
    else:
      cols = copy.deepcopy(ProfileCore.disp_columns)

    v = UserView(user_db_id = udb,config=yaml.dump(cols))
    v.put()
    id= v.key().id()
    v.name=u'ビュー('+str(id)+')'
    v.put()
    return v
