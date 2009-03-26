#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.document import Document
from model.category import Category
from model.site import Site
from model.page import Page

class DocumentController(BaseController):
    def show(self):
     self.site = Site.all().get()
     try:
       self.doc = db.GqlQuery("SELECT * FROM Document WHERE document_id = :1",self.params.get('id')).get()
       if self.doc.category_id:
         self.category = db.GqlQuery("SELECT * FROM Category where category_id= :1",self.doc.category_id).get()

     except Exception, ex:
        self.render(text='Exception: %s' % ex)

    def create(self):
     try:
        category = self.params.get('category')
        doc = Document(name=self.params['name'], category_id=category,document_id=self.params.get('document_id'))
        doc.put()

        self.redirect('/site/document/')
     except Exception, ex:
        self.render(text='Exception: %s' % ex)

    def delete(self):
      key = self.params.get("key");
      res= {"status":"success","msg":"削除しました"}
      document = Document.get(key);
      if document:
        document.delete()
      else:
        res= {"status":"error","msg":"削除に失敗しました"}
      self.render(json=self.to_json(res))

    def edit(self):
     self.categories = Category.all().order('-post_at')
     self.rec = Document.get(self.params.get('id'))
     self.pages = db.GqlQuery("SELECT * FROM Page WHERE document = :1 ORDER BY order",db.Key(self.params.get('id')))

    def update(self):
        doc = Document.get(self.params.get('key'))

        published = self.params.get('published')
        if published != None and published == "True":
          doc.published=True
        else:
          doc.published=False

        doc.name= self.params.get('name')
        doc.categoey_id = self.params.get('category_id')
        c = db.GqlQuery("SELECT * FROM Category WHERE category_id = :1",doc.category_id).get()
        doc.category_name = c.name
        doc.content = self.params.get('content')
        doc.document_id  = self.params.get('document_id')
        doc.put()

        self.redirect('/document/edit/'+ self.params.get('key'))
