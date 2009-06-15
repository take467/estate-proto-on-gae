#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users

from gaeo.controller import BaseController
from model.user_db import UserDb
from model.view    import UserView
from model.profile import ProfileCore
from model.share_user import ShareUser

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

    def search_refinement(self):
        
        self.view = None
        if self.v_id:
          self.view = UserView.get_by_id(int(self.v_id))
      
        self.fields = []
        self.width = 33
        
        i = 1
        if self.view and self.view.user_db_id.user == self.user:

          configs =  yaml.load(self.view.config)
          for col in configs: 
            if col['checked'] == 'checked':
              if 'hidden' not in col:
                col['hidden'] = 'false'
              elif col['hidden'] == '':
                col['hidden'] = 'false'

              if col['type'] == 'radio' or col['type'] == 'select':
                result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
                if result.count() > 0:
                  rec = result.get()
                  i = i+1
                  col['items'] = yaml.load(rec.yaml_data)
                  self.fields.append(col)

          m = 100 / i
          if m < self.width:
            self.width = m
        else:
          self.view = None

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
        results = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1",self.user.email())
        #results = ShareUser.all()
        for rec in results:
          if rec.share_view_id.key().id() == view.key().id(): 
            if rec.isDownloadable(): 
              canDL = True
              break

      if not canDL:
        self.render(text="不正なリクエスト(permission denied)")
        return

      results = ProfileCore.all().filter(' user_db_id =',view.user_db_id)
      config = yaml.load(view.config)

      # CSVのヘッダ情報
      line = []
      for col in config:
        if col['checked'] == 'checked':
          #line.append('"' + col['label']+'"')
          line.append('"' +  self.__conv(col['label'],'cp932') + '"')
      header= ','.join(line) + "\r\n"

      self.skip_rendering()
      res = self.getResponse()
      res.headers['Content-Type'] = "application/x-csv;charset:Shift_JIS"
      #res.headers['Content-Type'] = "application/octet-stream"
      if self.params.get('ie','false') == 'true' :
        res.headers["Content-Disposition"]="attachment; filename=" + self.params.get('filename') + ".csv"

      #res.out.write(header.encode('cp932'))
      res.out.write(header)

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

      self.config = []
      self.must_config = []
      for c in yaml.load(self.view.config):
        if not c['name'].startswith('iq_'):
          if c['name'] == 'email':
            self.must_config.append(c)
          else:
            self.config.append(c)
        else:
          if c['name'] != 'iq_content':
            self.must_config.append(c)

      if self.view.user_db().service_type == 'c':
        self.render(template="inquiry_edit")


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
        if col['name'].startswith('iq_'):
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

      # 問い合わせだったら必須項目が表示されないように削除
      self.config = []
      self.must_config = []
      if self.view.user_db().service_type == 'c':
        for c in yaml.load(self.view.config):
          if not c['name'].startswith('iq_'):
            if c['name'] == 'email':
              self.must_config.append(c)
            else:
              self.config.append(c)
          else:
            if c['name'] != 'iq_content':
              self.must_config.append(c)
        self.render(template="inquiry_update")



    def create(self):
       res= {"status":"success"}
     #try:
       udb = UserDb.get_by_id(int(self.params.get('db_id')))
       if udb:
         v = UserView.newInstance(udb)
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

    def __guess_charset(self,data):
      f = lambda d, enc: d.decode(enc) and enc

      try: return f(data, 'utf-8')
      except: pass
      try: return f(data, 'shift-jis')
      except: pass
      try: return f(data, 'euc-jp')
      except: pass
      try: return f(data, 'iso2022-jp')
      except: pass
      return None

    def __conv(self,data,enc):
      charset = self.__guess_charset(data)
      u = data
      if charset:
        u = data.decode(charset)
      return u.encode(enc)
