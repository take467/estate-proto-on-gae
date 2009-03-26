#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class Genre(BaseModel):
  genre_code = db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  post_at = db.DateTimeProperty(auto_now_add=True)

  def products(self):
    list = None

    s = "SELECT * FROM Product WHERE genre_id = :1 ORDER BY release_at DESC"
    q = db.GqlQuery(s,self.category_id,True)
    if q.count() > 0:
     list = q
    return list
