#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.controller import BaseController

from model.site import Site
from model.user_db import UserDb
from model.view import UserView
from google.appengine.api import users

class GroupsController(BaseController):
    def before_action(self):
      self.user = users.get_current_user()
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
      if g:
        g.delete()

      data = {'status':'success'}
      self.render(json=self.to_json(data))

    def create(self):
      data = {'status':'error'}
      try:
        if self.request.method.upper() != "POST":
          data = {'status':'error','msg':'forbidden method '}
        else:
          category = UserDb(user=self.user)
          category.put()
          data = {'status':'success','id':category.key().id(),'name':category.name}
      except ex:
        data = {'status':'error','msg':ex}
        
      self.render(json=self.to_json(data))
