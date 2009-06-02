#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController
from google.appengine.ext import db

from google.appengine.api import users
from model.profile import ProfileCore
from model.view    import UserView
from model.share_user    import ShareUser
from model.user_db import *

import json
from google.appengine.api import images
from getimageinfo import getImageInfo
import yaml
from google.appengine.api import users
from types import *
import datetime

class InquiryController(BaseController):

    def before_action(self):
      self.user = user=users.get_current_user()
      if 'cv_id' in self.cookies:
        self.v_id = self.cookies['cv_id']

    def delete(self):
      user=users.get_current_user()
      items = self.params.get('items')
      # split by ','
      msg = {'status':'success'}
      for id in items.split(','):
          if id != None and id != '':
            data = ProfileCore().get_by_id(int(id))
            #data = db.GqlQuery("SELECT * FROM ProfileCore WHERE  user = :1 and id = :2",user,int(id)).get()
            if data and data.user == user:
              data.delete()
            else:
              msg = {'status':'error','msg':'不正な操作です(' + str(data) + ')'}

      self.render(json=self.to_json(msg))

    def update(self):
      id = self.params.get('profile_id')
      v  = self.params.get('user_view_id')
      view = UserView.get_by_id(int(v))

      rec = ProfileCore.get_by_id(int(id))
      #データの所有者が違う場合は共有利用しているデータベースかチェック
      #もでるに隠蔽するべきか。
      # あと、本当に権限があるかShareUser.config を取得してチェックすべき！
      editable = False
      if rec.user != self.user and rec.user_db_id.user != self.user:
       sv = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",self.user.email(), view).get()
       if sv:
         if rec.user_db_id.key() == sv.share_view_id.user_db_id.key():
           editable = True
      else:
           editable = True

      if editable:
        config = yaml.load(view.config)
        for col in config:
          if col['checked'] == 'checked':
            val = self.params.get(col['name'])
            if val and val != '':
              setattr(rec,col['name'],val)
        rec.put()
      data = {'status':'success','flexReload':'true'}
      self.render(json=self.to_json(data))

    def edit(self):
      self.action_url = "/profile/update"
      id = self.params.get('id')
      v  = self.params.get('v')
      self.fields = []
      if id:
        self.profile_id = id
        self.view = UserView.get_by_id(int(v))
        data = ProfileCore.get_by_id(int(id))


        #データの所有者が違う場合は共有利用しているデータベースかチェック
        editable = False
        if data.user != self.user and data.user_db_id.user != self.user:
         sv = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",self.user.email(), self.view).get()
         if sv:
           #self.dump2=[data.user_db_id.key().id(),sv.share_view_id.user_db_id.key().id()]
           if data.user_db_id.key() == sv.share_view_id.user_db_id.key():
             editable = True
        else:
             editable = True

        if editable:
          self.config = yaml.load(self.view.config)
          for col in self.config:
            if col['checked'] == 'checked':
              col['val'] = getattr(data,col['name'])
              if col['type'] == 'radio' or col['type'] == 'select':
                 result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
                 if result.count() > 0: 
                   rec = result.get()
                   items = yaml.load(rec.yaml_data)
                   for item in items:
                     if item['code'] == col['val']:
                       if col['type'] == 'radio':
                         item['checked'] = 'checked'
                       elif col['type'] == 'select':
                         item['selected'] = 'selected'
                   col['items'] = items
           
              self.fields.append(col)
        self.dump = yaml.dump(self.fields)
        self.render(template="new")

    def new(self):
      self.action_url = "/profile/create"
      #id = self.params.get('id')
      id = self.v_id
      self.fields = []
      if id:
        self.view = UserView.get_by_id(int(id))
        self.config = yaml.load(self.view.config)
        data = ProfileCore(user_db_id=self.view.user_db_id,user=self.user,status="active",sex="0")
        for col in self.config:
          if col['checked'] == 'checked':
            col['val'] = getattr(data,col['name'])
            if col['type'] == 'radio' or col['type'] == 'select':
               result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
               if result.count() > 0: 
                 rec = result.get()
                 items = yaml.load(rec.yaml_data)
                 for item in items:
                   if col['type'] == 'radio' and item['code'] == col['val']:
                     item['checked'] = 'checked'

                 col['items'] = yaml.load(rec.yaml_data)
            self.fields.append(col)
        self.dump = yaml.dump(self.fields)

    def create(self):
      view_id = self.params.get('user_view_id')
      view = UserView.get_by_id(int(view_id))

      config = yaml.load(view.config)
      rec = ProfileCore(user_db_id=view.user_db_id,user=users.get_current_user())
      for col in config:
        if col['checked'] == 'checked':
          val = self.params.get(col['name'])
          if val:
            setattr(rec,col['name'],val)

      rec.put()
      data = {'status':'success','flexReload':'true'}
      self.render(json=self.to_json(data))

    def json(self):
      data = {'page':1, 'total': 0, 'rows': [] }
      self.render(json=self.to_json(data))

'''
      id = self.cookies['cv_id']

      if id == None:
        self.render(json=self.to_json([]))
        return

      self.fields = []
      self.view = UserView.get_by_id(int(id))
      if self.view == None:
        self.render(json=self.to_json([]))
        return

      # ビューの所有者とカレントのユーザが同じでなければ共有されたビュー
      user = self.user
      if self.view.user_db_id.user != self.user:
         sv = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",self.user.email(), self.view).get()
         if sv:
           user = sv.share_view_id.user_db_id.user

      self.config = yaml.load(self.view.config)

      query = self.params.get("query")
      qtype = self.params.get("qtype")

      sortname = self.params.get("sortname")
      if sortname == None or sortname == '':
        sortname = 'id'
      sortorder = self.params.get("sortorder")

      lines = int(self.params.get("rp"))
      page = int(self.params.get("page"))
      offset = (page - 1) * lines

      # 絞り込み項目が選択されていれば追加
      add_filters =[]
      if self.view:
        configs =  yaml.load(self.view.config)
        for col in configs:
          if col['checked'] == 'checked':
            if col['type'] == 'radio' or col['type'] == 'select':
              if isinstance(getattr(ProfileCore,col['name']),db.StringProperty):
                 val = self.params.get(col['name'])
                 if val != None and val != '':
                   add_filters.append({'name':col['name'],'val':val})

      results = []
      if (query != None and query != '' ) and ( qtype != None and qtype != ''):
        if qtype == 'id':
          p = None
          try:
            p  = ProfileCore.get_by_id(int(query))
          except:
            pass
          total = 0
          if p != None and (p.user == user):
            total = 1
            results.append(p)
        else:
          p = ProfileCore.all()
          p.filter(" user_db_id = ",self.view.user_db_id)
          #p.filter(" user = ",user)
          p.filter(qtype + " = ",query)
          for f in add_filters:
            p.filter(f['name'] + " = ",f['val'])

          results=p.fetch(lines,offset)
          total = p.count()
      else:
        p = ProfileCore.all()
        p.filter(" user_db_id = ",self.view.user_db_id)
        #p.filter(" user = ",user)
        for f in add_filters:
          p.filter(f['name'] + " = ",f['val'])
        is_id_sort = False
        if sortname != 'id' and sortname != '-id' :
          if sortorder.upper() == 'DESC':
            sortname = '-' + sortname
          p.order(sortname)
        else:
          is_id_sort = True

        results = p.fetch(lines,offset)
        total=p.count()
        if is_id_sort and (sortorder != None and sortorder.upper() == 'DESC'):
          results.reverse()

      rows = []
      for rec in results:
        wk = {'id':rec.key().id(),"cell":[rec.key().id()]}
        for col in self.config:
          if col['checked'] == 'checked':
            val = getattr(rec,col['name'])
            if col['type'] == 'radio' or col['type'] == 'select':
              udm = db.GqlQuery("SELECT  * FROM UserDbMaster WHERE name = :1",col['name']).get()
              for item in yaml.load(udm.yaml_data):
                if item['code'] == val:
                  val = item['name']
            if isinstance(getattr(ProfileCore,col['name']),db.DateTimeProperty):
              wk2 = val + datetime.timedelta(hours=9)
              if 'format' in col:
                val = wk2.strftime(col['format'])
              else:
                val = wk2.strftime('%Y/%m/%d %H:%M:%S')
                 
            wk['cell'].append(val)

        rows.append(wk)

      data = {'page':page, 'total': total, 'rows': rows }
      self.render(json=self.to_json(data))
'''
