#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.user_db import UserDb
from model.view    import UserView
from model.profile import ProfileCore

import yaml
import copy

class ViewController(BaseController):
    def edit(self):
      self.view = UserView.get_by_id(int(self.params.get('id')))
      self.config = yaml.load(self.view.config)
      pass

    def update(self):
      id = self.params.get('edit_view_id')
      name = self.params.get('view_name')

      # build yaml for config
      self.view = UserView.get_by_id(int(self.params.get('edit_view_id')))
      config = yaml.load(self.view.config)
      for col in config:
        key = "disp_%s" % col['name']
        val = self.params.get(key)
        if val == 'yes':
          col['checked']= 'checked'
        else:
          col['checked']= ''

      self.view.name = name
      self.view.config = yaml.dump(config)
      self.view.put()
      self.config = config
          

      pass

    def create(self):
       res= {"status":"success"}
     #try:
       udb = UserDb.get_by_id(int(self.params.get('db_id')))
       if udb:
         cols = copy.deepcopy(ProfileCore.disp_columns)
         config = yaml.dump(cols)
         v = UserView(user_db_id=udb,config=config)
         v.put()
       else:
         res= {"status":"error","msg":"missing user db"}
     #except Exception, ex:
     #   # 例外メッセージを表示する
     #  res= {"status":"error","msg":"Exception: %s" % ex}

       self.render(json=self.to_json(res))

    def delete(self):
      res= {"status":"success"}
      v = UserView.get_by_id(int(self.params.get('id')))
      v.delete()
      self.render(json=self.to_json(res))


'''
    def show(self):
      self.site = Site.all().get()
      self.category = db.GqlQuery("SELECT * FROM Category WHERE category_id = :1",self.params.get('id')).get()

    def update(self):
      self.rec = Category.get(self.params.get('key'))
      self.rec.content = self.params.get('content')
      self.rec.put()
      
      self.redirect('/category/edit/' + self.params.get('key'))
      pass


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
'''
