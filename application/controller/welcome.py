#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController

from google.appengine.api import users
from google.appengine.ext import db
from model.user_db import UserDb
from model.view import UserView

class WelcomeController(BaseController):

    def before_action(self):
      user = users.get_current_user()
      self.user_dbs = []
      for u in db.GqlQuery("SELECT * FROM UserDb WHERE user = :1",user):
        list = db.GqlQuery("SELECT * FROM UserView WHERE user_db_id = :1",u)
        self.user_dbs.append({'db':u,'views':list})

    def index(self):
      pass
