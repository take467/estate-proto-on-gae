#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController

from model.profile_group import ProfileGroup
from google.appengine.api import users
from google.appengine.ext import db

class WelcomeController(BaseController):

    def before_action(self):
      user = users.get_current_user()
      self.groups = [{'id':'0','name':'全カテゴリ','views':[{'id':'0','name':'全データ'},{'id':'1','name':'2009年'}]}]
      for c in db.GqlQuery("SELECT * FROM ProfileGroup WHERE user = :1",user):
        self.groups.append({'id':c.key().id(),'name':c.name})

    def index(self):
      pass
