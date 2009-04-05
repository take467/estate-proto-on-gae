#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController

from google.appengine.api import users
from google.appengine.ext import db
from model.user_db import UserDb
from model.profile import *
from model.view import UserView
import yaml

class WelcomeController(BaseController):

    #def before_action(self):
    #  user = users.get_current_user()
    #  self.user_dbs = []
    #  for u in db.GqlQuery("SELECT * FROM UserDb WHERE user = :1",user):
    #    list = db.GqlQuery("SELECT * FROM UserView WHERE user_db_id = :1",u)
    #    self.user_dbs.append({'db':u,'views':list})
    def index(self):
      v_id = self.params.get('v')
      if v_id:
        self.colModels = []
        self.searchitems = []
        self.view = UserView.get_by_id(int(v_id))
        if self.view: 
          self.colModels.append({'name':'id','label':'ID','width':'20','align':'center'})
          for col in yaml.load(self.view.config):
            if col['checked'] == 'checked':
              self.colModels.append(col)
              if col['type'] != 'radio' and col['type'] != 'select':
                if  isinstance(getattr(ProfileCore,col['name']),db.StringProperty):
                  self.searchitems.append({'display':col['label'],'name':col['name']})

      else:
        pass
