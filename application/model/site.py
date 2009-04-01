#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class Site(BaseModel):
  logo_label = db.StringProperty(required=True)
  logo_subtext = db.StringProperty()
  description = db.StringProperty(required=True)
  keywords = db.StringProperty()
  content = db.TextProperty()
  sidebar_label = db.StringProperty()
  sidebar_content = db.TextProperty()
  g_navi_categories = db.ListProperty(db.Key)
  b_navi_categories = db.ListProperty(db.Key)
  post_at  = db.DateTimeProperty(auto_now_add=True)

  def bottom_navi_categories(self):
    list = []
    for key in self.b_navi_categories:
      c = Category.get(key)
      list.append(c)

    if len(list) > 0:
      return list
    else:
      return None

  def global_navi_categories(self):
    list = []
    for key in self.g_navi_categories:
      c = Category.get(key)
      list.append(c)

    if len(list) > 0:
      return list
    else:
      return None
