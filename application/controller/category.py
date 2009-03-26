#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController

from model.category import Category
from model.site import Site
from model.document import Document

class CategoryController(BaseController):
    def create(self):
     try:
        categories = Category.all()
        for category in categories:
          name = self.params.get("name_%s" % category.category_id)
          id = self.params.get("category_%s" % category.category_id)
          wk = db.GqlQuery("SELECT * FROM Category WHERE category_id = :1",id).get()
          if wk != None:
            category.name=name
            category.category_id = id
            category.put()

        new = self.params['new_category']
        if new:
          id = self.params['new_category_id']
          category = Category(name=new, category_id=id,order=max)
          category.put()

        # URL '/category/' にリダイレクト
        self.redirect('/site/category/')
     except Exception, ex:
        # 例外メッセージを表示する
        self.render(text='Exception: %s' % ex)

    def show(self):
      self.site = Site.all().get()
      self.category = db.GqlQuery("SELECT * FROM Category WHERE category_id = :1",self.params.get('id')).get()

    def edit(self):
      self.rec = Category.get(self.params.get('id'))

    def update(self):
      self.rec = Category.get(self.params.get('key'))
      self.rec.content = self.params.get('content')
      self.rec.put()
      
      self.redirect('/category/edit/' + self.params.get('key'))
      pass

    def delete(self):

      key = self.params.get("key");

      # カテゴリに属するドキュメントがあったら削除できない
      res= {"status":"success","msg":"削除しました"}
      query = db.GqlQuery("SELECT * FROM Document WHERE category = :1",db.Key(key))
      if query.count() > 0:
        res= {"status":"error","msg":"カテゴリに属するドキュメントがあるため削除できません。"}
      else:
        category = Category.get(db.Key(key));
        if category:
          category.delete()
          # リナンバー
          query = Category.all();
          num = 1;
          for c in query:
            c.order = num
            c.put()
            num = num +1
        else:
          res= {"status":"error","msg":"削除に失敗しました"}

      self.render(json=self.to_json(res))
