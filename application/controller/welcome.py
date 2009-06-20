#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController

from google.appengine.api import users
from google.appengine.ext import db
from model.user_db import UserDb
from model.profile import *
from model.inquiry import *
from model.view import UserView
from model.share_user import ShareUser
import yaml

class WelcomeController(BaseController):

    def before_action(self):
      self.user = users.get_current_user()
      self.logout_url =  users.create_logout_url('/')
    #  self.user_dbs = []
    #  for u in db.GqlQuery("SELECT * FROM UserDb WHERE user = :1",user):
    #    list = db.GqlQuery("SELECT * FROM UserView WHERE user_db_id = :1",u)
    #    self.user_dbs.append({'db':u,'views':list})
    def greeting(self):
      pass
    
    def index(self):
      v_id = None
      if 'cv_id' in self.cookies:
        v_id = self.cookies['cv_id'] 

      self.colModels = []
      self.searchitems = []
      if v_id:
        self.view = UserView.get_by_id(int(v_id))
        if self.view == None:
          self.response.headers.add_header('Set-Cookie','cv_id=-1 ;expires=Fri, 5-Oct-1979 08:10:00 GMT')

        self.fields = []

        self.width = 33
        i = 1
        #if self.view and self.view.user_db_id.user == self.user: 
        if self.view:
          self.auth = {'w':True,'d':True,'dl':True}
          if self.view.user_db_id.user != self.user: 
            # 共有ビュー？
            v = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",self.user.email(),self.view).get()
            if v:
              # 権限の設定
              config = yaml.load(v.config)
              for item in config:
                self.auth[item['name']] = item['val']
            else:
              self.view = None
              return

          self.colModels.append({'display':'ID','name':'id','width':'40','align':'center','hidden':'false','sortable':'true'})

          configs =  yaml.load(self.view.config)
          names = []
          for col in configs:

            if col['search_refinement'] and col['checked'] == 'checked':
              result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
              if result.count() > 0:
                rec = result.get()
                i = i+1
                col['items'] = yaml.load(rec.yaml_data)
                self.fields.append(col)
                names.append('#sr_' + col['name'])

            if col['name'].startswith('iq_') and col['checked'] == 'checked':
              self.colModels.append({'display':col['label'],'name':col['name'],'width':'100','align':'left','hidden':col['hidden'],'sortable':'true'})
              continue
            if col['name'] == 'email':
              self.colModels.append({'display':col['label'],'name':col['name'],'width':col['width'],'align':col['align'],'hidden':col['hidden'],'sortable':'true'})
              continue

            if col['checked'] == 'checked':
              if 'hidden' not in col:
                col['hidden'] = 'false'
              elif col['hidden'] == '':
                col['hidden'] = 'false'

              self.colModels.append({'display':col['label'],'name':col['name'],'width':col['width'],'align':col['align'],'hidden':col['hidden'],'sortable':'true'})
              if col['type'] != 'radio' and col['type'] != 'select':
                if col['name'].startswith('iq_'):
                  # "iq_{name} => {name}
                  name = col['name'][3:]
                  if isinstance(getattr(Inquiry,name),db.StringProperty):
                    self.searchitems.append({'display':col['label'],'name':col['name']})
                else:
                  if isinstance(getattr(ProfileCore,col['name']),db.StringProperty):
                    self.searchitems.append({'display':col['label'],'name':col['name']})


          self.fields_join = ','.join(names)
          self.colModelsJson = self.to_json(self.colModels)
          m = 100 / i
          if m < self.width:
            self.width = m
      
        else:
          self.view = None
          self.colModelsJson = None
