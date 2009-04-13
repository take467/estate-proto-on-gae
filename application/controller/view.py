#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users

from gaeo.controller import BaseController
from model.user_db import UserDb
from model.view    import UserView
from model.profile import ProfileCore

import yaml
import copy

class ViewController(BaseController):
    def before_action(self):
      self.user = users.get_current_user()
      self.v_id = None
      if 'cv_id' in self.cookies:
        self.v_id = self.cookies['cv_id']
      pass

#    def cols(self):
#      colModels=[]
#      if self.v_id:
#        view = UserView.get_by_id(int(self.v_id))
#        configs =  yaml.load(view.config)
#        colModels.append({'name':'id','label':'ID','width':'20','align':'center','hidden':'false'})
#        for col in configs:
#          if col['checked'] == 'checked':
#            if 'hidden' not in col:
#              col['hidden'] = 'false'
##            elif col['hidden'] == '':
#              col['hidden'] = 'false'
#
#            colModels.append(col)
#      self.render(json=self.to_json(colModels))


    def share(self):
      id = self.params.get('id')
      if id == None:
        self.render(text='不正なリクエスト')
        return

      self.view = UserView.get_by_id(int(id))
 
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
        if col['type'] == 'hidden':
          continue
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

    #def reset(self):
    #  cols = copy.deepcopy(ProfileCore.disp_columns)
    #  config = yaml.dump(cols)
    #  v = UserView.get_by_id(id)
    #  if v.user_db_id.user == self.user:
    #     v.config = config
    #     v.put()

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

