#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController

from model.page import Page
from model.document import Document

class PageController(BaseController):
    def create(self):
     #try:
        document = Document.get(self.params.get('document'))
        page = Page(  name=self.params.get('name'),
                      document=document,
                      content=self.params.get('content'),
                      order=int(self.params.get('order'))
              )
        # データの保存
        page.put()

        # URL '/page/' にリダイレクト
        self.redirect('/document/edit/'+self.params.get('document') )
     #except Exception, ex:
     #   # 例外メッセージを表示する
     #   self.render(text='Exception: %s' % ex)

    def new(self):
	query = db.GqlQuery("SELECT * FROM Page ORDER BY order DESC")
	self.page_num = 1
	if query.count() > 0:
	  page = query.get()
	  self.page_num = page.order + 1
        self.document = Document.get(self.params.get('id'))

    def show(self):
        self.site = Site.all().get();
        self.categories = Category.all().order('order').get()
        self.rec = Page.get(self.params.get('id'))
