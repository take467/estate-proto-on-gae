#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel
from model.document import Document

class Category(BaseModel):
  category_id = db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  content = db.TextProperty()
  post_at = db.DateTimeProperty(auto_now_add=True)
  doc_fetch_limit = db.IntegerProperty(default=10)

  def documents(self):
    list = None

    s = "SELECT * FROM Document WHERE category_id = :1 and published = :2 ORDER BY post_at DESC"
    q = db.GqlQuery(s,self.category_id,True)
    if q.count() > 0:
     list = q
    return list

  def documents_with_limit(self):
    list = None

    s = "SELECT * FROM Document WHERE category_id = :1 and published = :2 ORDER BY post_at DESC LIMIT %s" % self.doc_fetch_limit
    q = db.GqlQuery(s,self.category_id,True)
    if q.count() > 0:
     list = q
    return list
