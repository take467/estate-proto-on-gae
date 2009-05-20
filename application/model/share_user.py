#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.view import UserView

class ShareUser(BaseModel):
  share_view_id  = db.ReferenceProperty(UserView)
  email          = db.StringProperty()
  config         = db.TextProperty()

  default_config = [{'name':'w','val':False},{'name':'d','val':False},{'name':'dl','val':False}]

  def isWritable(self):
    return __getVal('w')

  def isDownloadable(self):
    return __getVal('dl')

  def isDeletable(self):
    return __getVal('d')

  def _getVal(self,key):
    prop =  yaml.load(self.config)
    for h in prop:
       if h['name'] == key:
         return h['val']
