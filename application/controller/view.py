#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users

from gaeo.controller import BaseController
from model.user_db import UserDb
from model.view    import UserView
from model.profile import ProfileCore

import yaml
import copy
import logging
import datetime

from google.appengine.ext.webapp import template

class ViewController(BaseController):
    def before_action(self):
      self.user = users.get_current_user()
      self.v_id = None
      if 'cv_id' in self.cookies:
        self.v_id = self.cookies['cv_id']
      pass

    def import_csv(self):
      if self.request.method.upper() == "GET":
        self.view = UserView.get_by_id(int(self.params.get('id')))
        pass

      if self.request.method.upper() == "POST":
        data={'status':'success','msg':'アップロードが完了しました'}
        view = UserView.get_by_id(int(self.params.get('edit_view_id')))

        view.data = self.params.get('file')
        view.put()
        

        if self.v_id == self.params.get('edit_view_id'):
          data['flexReload']='true'

        self.render(json=self.to_json(data))
        pass

    def export(self):
      id = self.params.get('id')
      if id == None:
        self.render(text='不正なリクエスト')
        return

      view = UserView.get_by_id(int(id))
      # 所有者 or 権限のあるユーザかチェック

      canDL = False
      if self.user == view.user_db_id.user:
        canDL = True
      else:
        view.getProperty
        su = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",self.user.email(), view.key().id()).get()
        if su.isDownloadable(): 
          canDL = True

      if not canDL:
        self.render(text="不正なリクエスト(permission denied)")
        return

      results = ProfileCore.all().filter(' user_db_id =',view.user_db_id)
      config = yaml.load(view.config)

      # CSVのヘッダ情報
      line = []
      for col in config:
        if col['checked'] == 'checked':
          line.append('"' + col['label']+'"')
      header= ','.join(line) + "\r\n"

      self.skip_rendering()
      res = self.getResponse()
      res.headers['Content-Type'] = "application/x-csv;charset:Shift_JIS"
      #res.headers['Content-Type'] = "application/octet-stream"
      if self.params.get('ie','false') == 'true' :
        res.headers["Content-Disposition"]="attachment; filename=" + self.params.get('filename') + ".csv"

      res.out.write(header.encode('cp932'))

      for rec in results:
        line = []
        for col in config:
          if col['checked'] == 'checked':
            val = getattr(rec,col['name'])
            #if col['type'] == 'radio' or col['type'] == 'select':
            #  udm = db.GqlQuery("SELECT  * FROM UserDbMaster WHERE name = :1",col['name']).get()
            #  for item in yaml.load(udm.yaml_data):
            #    if item['code'] == val:
            #      val = item['name']
            if isinstance(getattr(ProfileCore,col['name']),db.DateTimeProperty):
              wk2 = val + datetime.timedelta(hours=9)
              if 'format' in col:
                val = wk2.strftime(col['format'])
              else:
                val = wk2.strftime('%Y/%m/%d %H:%M:%S')
            line.append('"' + val.replace('"','""') + '"')
        wk = ','.join(line) + "\r\n"
        res.out.write(wk.encode('cp932'))

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

      logging.debug("[ViewController#update] (params)="+ self.to_json(self.params) +")")

      # build yaml for config
      if not id:
        return

      self.view = UserView.get_by_id(int(self.params.get('edit_view_id')))
      config = yaml.load(self.view.config)
      for col in config:
        if col['type'] == 'hidden':
          continue
        key = "disp_%s" % col['name']
        val = self.params.get(key,'None')

        if val == 'yes':
          col['checked']= 'checked'
        else:
          col['checked']= ''

      self.view.name = name
      self.view.config = yaml.dump(config)
      self.view.put()
      self.config = config

    #self.render(json=self.to_json({'status':'success'}))


    def create(self):
       res= {"status":"success"}
     #try:
       udb = UserDb.get_by_id(int(self.params.get('db_id')))
       if udb:
         cols = copy.deepcopy(ProfileCore.disp_columns)
         config = yaml.dump(cols)
         v = UserView(user_db_id=udb,config=config)
         v.put()
         res= {"status":"success",'cv_id':v.key().id(),'r':'/'}
       else:
         res= {"status":"error","msg":"missing user db"}
     #except Exception, ex:
     #   # 例外メッセージを表示する
     #  res= {"status":"error","msg":"Exception: %s" % ex}

       self.render(json=self.to_json(res))

    def delete(self):
      res= {"status":"success",'reload':'true'}
      #logging.debug('deleting view(' + self.params.get('id') + ')')
      v = UserView.get_by_id(int(self.params.get('id')))
      v.delete()
      self.render(json=self.to_json(res))

