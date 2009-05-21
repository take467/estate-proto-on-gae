#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.view import UserView
import yaml

class ShareUser(BaseModel):
  share_view_id  = db.ReferenceProperty(UserView)
  email          = db.StringProperty()
  config         = db.TextProperty()

  default_config = [{'name':'w','val':'false'},{'name':'d','val':'false'},{'name':'dl','val':'false'}]

  def isWritable(self):
    return self.__getVal('w')

  def isDownloadable(self):
    return self.__getVal('dl')

  def isDeletable(self):
    return self.__getVal('d')

  def __getVal(self,key):
    prop =  yaml.load(self.config)
    result = False
    for h in prop:
       if h['name'] == key:
         result = h['val'] == 'true'
         break

    return result
