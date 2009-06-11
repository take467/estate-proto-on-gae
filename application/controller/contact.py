#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.user_db import *
from model.inquiry import *
from model.notice_mail import *

import re
import cgi
import copy

class ContactController(BaseController):
    def before_action(self):
      # かならずURLの最後にはUserDbのIDが付与される
      self.udb = UserDb.get_by_id(int(self.params.get('id')))

      self.server_name = self.request.environ['SERVER_NAME']
      self.server_port = int(self.request.environ['SERVER_PORT'])
      if self.server_port != 80:
        self.base_url = ('http://%s:%s/' % (self.server_name, self.server_port))
      else:
        self.base_url = 'http://%s/' % (self.server_name,)

    def confirm(self):
      # チケットの確認
      #try:
      #  ticket = self.session['ticket']
      #  if ticket == None:
      #    self.redirect('/contact/preview/' + str(self.udb.key().id()))
      #    return
      #except:
      #  self.redirect('/contact/preview/' + str(self.udb.key().id()))
      #  return

      self.action_url = self.base_url + "contact/post/" + str(self.udb.key().id())

      # FORM FIELD の更新
      self.form_fields = []
      self.form_config = self.udb.getProperty('form_config')
      for col in self.form_config:
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):

          col['val'] = re.sub("\n","<br/>",cgi.escape(self.params.get(col['name'])))

          if col['type'] == 'radio' or col['type'] == 'select':
            result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
            if result.count() > 0:
              rec = result.get()
              for item in yaml.load(rec.yaml_data):
                if item['code'] == col['val']:
                  col['code'] = item['code']
                  col['val'] = item['name']
          self.form_fields.append(col)

      # 確認ページ（HTMLチャンク) が表示される 


    def preview(self):
      pass

    def form(self):
      self.action_url = self.base_url + "contact/confirm/" + str(self.udb.key().id())
      self.width = self.params.get('width','700')
      self.textarea_w = (int(self.width)  - 120) * 0.9
      # チケットの確認
      #ticket = None
      start_over = False
      #try:
      #  ticket = self.session['ticket']
      #except:
      #  pass

      #if ticket == None:
      #  # チケットの発行
      #  self.session['ticket'] = str(self.udb.key())
      #  self.session.put()
      #
      #elif ticket != None and self.request.method.upper() == "POST":

      if self.request.method.upper() == "POST":
        start_over = True

      self.fields = []
      self.form_config = self.udb.getProperty('form_config')
      for col in self.form_config:
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):
          if start_over:
            col['val']  = self.params.get(col['name'])
            if col['type'] == 'textarea':
               s = re.sub("<br/>","\n",self.params.get(col['name']))
               s = s.replace("&amp;", "&") # Must be done first!
               s = s.replace("&lt;","<")
               s = s.replace("&gt;",">")
               s = s.replace("&quot;",'"')
               col['val'] = s
          if col['type'] == 'radio' or col['type'] == 'select':
            result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
            if result.count() > 0:
              rec = result.get()
              items = yaml.load(rec.yaml_data)
              if start_over:
                for item in items:
                  if item['code'] == col['val']:
                    if col['type'] == 'radio':
                      item['checked'] = 'checked'
                    elif col['type'] == 'select':
                      item['selected'] = 'selected'
              col['items'] = items

          self.fields.append(col)

    # 問い合わせを保存
    def post(self):
      # チケットの確認
      #try:
      #  ticket = self.session['ticket']
      #  if ticket == None:
      #    self.redirect('/contact/preview/'+str(self.udb.key().id()))
#	  return
#      except:
#        self.redirect('/contact/preview/'+str(self.udb.key().id()))
#	return

#      try:
#        self.session['ticket']=None
#        del self.session['ticket']
#        self.session.put()
#      except KeyError ,ex:
#        self.render(text=ex) 
#        return

      profile = ProfileCore(user_db_id = self.udb,user=self.udb.user)
      profile.put()
      inquiry = Inquiry(user_db_id = self.udb,profile_id = profile)
      # FORM FIELD の更新
      self.form_config =  self.udb.getProperty('form_config')
      for col in self.udb.getProperty('form_config'):
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):

          name = col['name']
          val =self.params.get(name)
          if name.startswith('iq_'):
            name = name[3:]
            setattr(inquiry,name,val)
          else:
            setattr(inquiry.profile(),name,val)

      #inquiry.profile().put()
      inquiry.put() 

      # FORM FIELD の更新
      self.form_fields = []
      for col in self.form_config:
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):
          col['val'] = re.sub("\n","<br/>",cgi.escape(self.params.get(col['name'])))
          if col['type'] == 'radio' or col['type'] == 'select':
            result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
            if result.count() > 0:
              rec = result.get()
              for item in yaml.load(rec.yaml_data):
                if item['code'] == col['val']:
                  col['code'] = item['code']
                  col['val'] = item['name']
          self.form_fields.append(col)

      # ここで 送信者と問い合わせ担当者にメールを送る
      m = NoticeMail()
      m.notice(self.request,inquiry)
      m.send_confirm(self.request,inquiry)

      # 送信完了メッセージ（HTMLチャンク)を出力
