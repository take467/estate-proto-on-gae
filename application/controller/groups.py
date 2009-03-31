#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.controller import BaseController

from model.site import Site
from model.profile_group import ProfileGroup
from google.appengine.api import users

class GroupsController(BaseController):
    def before_action(self):
      self.user = users.get_current_user()
      pass

#    def index(self):
#      results = db.GqlQuery("SELECT * FROM ProfileGroup WHERE user = :1",self.user)
#
#      list = []
#      list.append({'id':'0','text':'<a href="#">全カテゴリ</a>','children':[{'classes':'file','text':'<a href="#">全データ</a>'}],'classes':'folder','expand':True})
#      for rec in results:
#        list.append({'id':rec.key().id(),'text':rec.name,'children':[],'classes':'folder','expand':True})
#
#      self.render(json=self.to_json(list))

    def update(self):
      if self.request.method.upper() != "POST":
        return 

      id = self.params.get('id')
      g = ProfileGroup.get_by_id(int(id))
      if g:
        g.name = self.params.get('name')
	g.put()

      data = {'status':'success'}
      self.render(json=self.to_json(data))

    def delete(self):
      if self.request.method.upper() != "POST":
        return 

      id = self.params.get('id')
      g = ProfileGroup.get_by_id(int(id))
      if g:
        g.delete()

      data = {'status':'success'}
      self.render(json=self.to_json(data))

    def create(self):
      if self.request.method.upper() != "POST":
        return 

      name = self.params.get('name')
      category = ProfileGroup(user=self.user,name=name)
      category.put()

      data = {'status':'success','id':category.key().id(),'name':category.name}
      self.render(json=self.to_json(data))
