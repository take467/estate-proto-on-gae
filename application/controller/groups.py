#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.controller import BaseController

from model.site import Site
from model.user_db import UserDb
from model.view import UserView
from model.profile import ProfileCore
from google.appengine.api import users
import yaml
import copy

class GroupsController(BaseController):
    def before_action(self):
      self.user = users.get_current_user()
      if 'cv_id' in self.cookies:
        self.v_id = self.cookies['cv_id']
      pass

    def treeview(self):
      user = users.get_current_user()
      self.user_dbs = []
      for u in db.GqlQuery("SELECT * FROM UserDb WHERE user = :1",user):
        list = db.GqlQuery("SELECT * FROM UserView WHERE user_db_id = :1",u)
        self.user_dbs.append({'db':u,'views':list})

      #list  = []
      #views = []
      #for u in db.GqlQuery("SELECT * FROM UserDb WHERE user = :1",self.user):
      #  for v in db.GqlQuery("SELECT * FROM UserView WHERE user_db_id = :1",u):
      #    views.append({'id':v.key().id(),"text":v.name})
      #  list.append({'id':u.key().id(),'text':u.name,'children':views,'classes':'folder','expand':True})
      #self.render(json=self.to_json(list))

    def edit(self):
      id = self.params.get('id')
      self.user_db = UserDb.get_by_id(int(id))
      pass

    def update(self):
      if self.request.method.upper() != "POST":
        return 

      id = self.params.get('id')
      g = UserDb.get_by_id(int(id))
      if g:
        g.name = self.params.get('name')
	g.put()

      data = {'status':'success'}
      self.render(json=self.to_json(data))

    def delete(self):
      if self.request.method.upper() != "POST":
        return 

      id = self.params.get('id')
      g = UserDb.get_by_id(int(id))

      if g.user != self.user:
        data = {'status':'error','msg':'権限がありません'}
        self.render(json=self.to_json(data))
        return

      data = {'status':'success'}
      if g:
        # 紐づくProfileデータは、リンク関係を切るー＞ゴミ箱をつくってそこに入れる
        q = ProfileCore.all()
        q.filter("user_db_id = ",g)
        for p in q:
          p.user_db_id = None
          p.put()

        # 紐づくViewを全て削除
        q = UserView.all()
        q.filter("user_db_id = ",g)
        for p in q:
          p.delete()

        g.delete()
        data = {'status':'success'}

        if id == self.v_id:
  	  self.response.headers.add_header('Set-Cookie','cv_id=-1 ;expires=Fri, 5-Oct-1979 08:10:00 GMT')

      self.render(json=self.to_json(data))

    def create(self):
        data = {'status':'error'}
      #try:
        if self.request.method.upper() != "POST":
          data = {'status':'error','msg':'forbidden method '}
        else:
          category = UserDb(user=self.user)
          category.put()
          # ついでにビューもつくってしまう
          cols = copy.deepcopy(ProfileCore.disp_columns)
          v = UserView(user_db_id = category,config=yaml.dump(cols))
          v.put()
          data = {'status':'success','id':category.key().id(),'name':category.name}
      #except Exception,ex:
      #   data = {'status':'error','msg':ex}
        
        self.render(json=self.to_json(data))
