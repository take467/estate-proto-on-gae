#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.view import UserView

class ShareUser(BaseModel):
  share_view_id  = db.ReferenceProperty(UserView)
  email          = db.StringProperty()
  config         = db.TextProperty()

  default_config = [{'name':'w','val':False},{'name':'d','val':False},{'name':'dl','val':False}]
