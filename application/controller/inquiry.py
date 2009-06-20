#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users

from gaeo.controller import BaseController
from model.user_db import *
from model.inquiry import *
from model.view import *

import re
import cgi
import copy
import logging
import datetime
import os
from google.appengine.api import mail

class InquiryController(BaseController):
    def before_action(self):
      self.server_name = self.request.environ['SERVER_NAME']
      self.server_port = int(self.request.environ['SERVER_PORT'])
      if self.server_port != 80:
        self.base_url = ('http://%s:%s/' % (self.server_name, self.server_port))
      else:
        self.base_url = 'http://%s/' % (self.server_name,)
      self.user=users.get_current_user()

    def css_form(self):
      self.udb = UserDb.get_by_id(int(self.params.get('id')))
      self.css = self.udb.getProperty('css')
      pass

    def update_css(self):
      if self.request.method.upper() != "POST":
        return
      
      data = {'status':'success','msg':'スタイルシートを保存しました'}
      self.udb = UserDb.get_by_id(int(self.params.get('id')))
      css = self.params.get('css_edit_area')
      self.udb.setProperty('css',css)
      self.udb.put()

      self.render(json=self.to_json(data))

    def preview(self):
      self.udb = UserDb.get_by_id(int(self.params.get('id')))
      self.w = self.params.get('w','700')
      self.h = self.params.get('h','550')
      pass

    def delete(self):
      view = UserView.get_by_id(int(self.cookies['cv_id']))
      items = self.params.get('items')
      # split by ','
      msg = {'status':'success'}
      for id in items.split(','):
        if id != None and id != '':
          data = Inquiry().get_by_id(int(id))

          # 権限チェックが必要
          if data.user_db_id.user == self.user:
            #所有者であれば無条件
            data.delete()
          else:
            #そうでなければ権限があるかチェック
            su = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",user.email(), view).get()
            if su.isDeletable():
              data.delete()
            else:
              msg = {'status':'error','msg':'不正な操作です(' + str(data) + ')'}

      self.render(json=self.to_json(msg))

    def send_reply(self):
      self.inquiry = Inquiry.get_by_id(int(self.params.get('iq_id')))
      self.view = UserView.get_by_id(int(self.params.get('v')))
      # 権限チェックが必要
      editable = False
      if self.inquiry.user_db_id.user == self.user:
        editable=True
      else:
        #そうでなければ権限があるかチェック
        su = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",user.email(), view).get()
        if su.isWritable():
          editable = True

      msg = {'status':'success','msg':'回答を送信しました','view_id':self.view.key().id(),'iq_id':self.inquiry.key().id()}
      if editable:

        # メール送信
        values = {'id':self.inquiry.key().id(), 'name':self.inquiry.profile().email,'reply_content':self.inquiry.reply_content}

        self.udb = self.view.user_db()
        # SUBJECT
        subject = '{{id}}'
        ts = self.udb.getProperty('reply_mail_subject')
        if ts:
          subject = self.render_txt(template_string=ts,values=values)
        else:
          subject = self.render_txt(template="reply_mail_subject",values=values)

        # BODY  
        body = '{{reply_content}}'
        ts = self.udb.getProperty('reply_mail_body')
        if ts:
          body = self.render_txt(template_string=ts,values=values)
        else:
          body    = self.render_txt(template="reply_mail_body",values=values)

        if mail.is_email_valid(self.inquiry.profile().email):
          mail.send_mail(sender=self.user.email(), to=self.inquiry.profile().email, subject=subject, body=body)
        else:
          msg = {'status':'error','msg':'不正な処メールアドレスです。(' + self.inquiry.profile().email + ')'}
          self.render(json=self.to_json(msg))
          return

        self.inquiry.reply_person = self.user.email()
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        self.inquiry.reply_at = now
        self.inquiry.status = 'answered'
        self.inquiry.put()

      else:
        msg = {'status':'error','msg':'不正な処理です'}

      self.render(json=self.to_json(msg))

    def save_reply(self):
      self.inquiry = Inquiry.get_by_id(int(self.params.get('iq_id')))
      self.view = UserView.get_by_id(int(self.params.get('v')))

      # 権限チェックが必要
      editable = False
      if self.inquiry.user_db_id.user == self.user:
        editable=True
      else:
        #そうでなければ権限があるかチェック
        su = db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1 and share_view_id = :2",user.email(), view).get()
        if su.isWritable():
          editable = True

      #msg = {'status':'success','msg':'回答を保存しました','view_id':self.view.key().id(),'iq_id':self.inquiry.key().id()}
      msg = {'status':'success','view_id':self.view.key().id(),'iq_id':self.inquiry.key().id()}
      if editable:
        #内部利用だし、JSでのチェックだけでとりあえず良いだろう
        self.inquiry.reply_content = self.params.get('reply_content')
        #now = datetime.datetime.now() + datetime.timedelta(hours=9)
        self.inquiry.reply_person = self.user.email()
        self.inquiry.put()
      else:
        msg = {'status':'error','msg':'不正な処理です'}

      self.render(json=self.to_json(msg))


    def edit(self):
      self.mode = self.params.get('mode','show')
      self.view = UserView.get_by_id(int(self.params.get('v')))
      self.inquiry = Inquiry.get_by_id(int(self.params.get('id')))
      #self.inquiry.content       = re.sub("\n","<br/>",cgi.escape(self.inquiry.content))
      if self.inquiry.reply_content == None or self.inquiry.reply_content == '':
        self.mode = 'edit'

      if self.inquiry.status == 'answered':
        self.mode='show' ;#強制的に変更

      #if self.mode == 'show':
        #self.inquiry.reply_content = re.sub("\n","<br/>",cgi.escape(self.inquiry.reply_content))


      self.option_cols = []
      for c in yaml.load(self.view.config):
        if not c['name'].startswith('iq_'):
          if c['name'] != 'email':
            if c['checked'] == 'checked':
              self.option_cols.append(c)
              val = getattr(self.inquiry.profile(),c['name'])
              if c['type'] == 'radio' or c['type'] == 'select':
                c['val'] = self.inquiry.profile().getLabel(c['name'],val)
              else:
                c['val'] = val
              



    def json(self):
      # ビューの確定
      id = self.cookies['cv_id']

      if id == None:
        self.render(json=self.to_json([]))
        return

      self.fields = []
      self.view = UserView.get_by_id(int(id))
      if self.view == None:
        self.render(json=self.to_json([]))
        return

      # inquiry 一覧を取得（flexigridの絞り込み条件に従って)
      self.config = yaml.load(self.view.config)

      query = self.params.get("query",'')
      qtype = self.params.get("qtype",'')

      sortname = self.params.get("sortname",'iq_id')
      if sortname.startswith("iq_"):
        sortname = sortname[3:]
      elif sortname.startswith("-iq_"):
        sortname = "-" + sortname[4:]
      sortorder = self.params.get("sortorder",'DESC')

      lines = int(self.params.get("rp",'15'))
      page = int(self.params.get("page",'1'))
      offset = (page - 1) * lines

      # 絞り込み項目が選択されていれば追加
      # Inquiry と Profileの両方の項目で絞り込みが発生するので、まずは
      # Inquiryをfetchしたあと自前でループしてPfrofile項目を絞り込む
      # RDBなら簡単なのに。。。
      add_filters =[]
      if self.view:
        #configs =  yaml.load(self.view.config)
        for col in self.config:
          if col['checked'] == 'checked':
            if col['type'] == 'radio' or col['type'] == 'select':

              flg = False
              if col['name'].startswith('iq_'): 
                # "iq_{name} => {name}
                name = col['name'][3:]
                if isinstance(getattr(Inquiry,name),db.StringProperty):
                  flg = True
              elif isinstance(getattr(ProfileCore,col['name']),db.StringProperty):
                  flg = True

              if flg:
                 val = self.params.get(col['name'])
                 if val != None and val != '':
                   add_filters.append({'name':col['name'],'val':val})

      results = []
      if (query != None and query != '' ) and ( qtype != None and qtype != ''):
        add_filters.append({'name':qtype,'val':query})

      p = None
      if (query != None and query != '' ) and  qtype == 'iq_id' and ( qtype != None and qtype != ''):
        try:
          p  = Inquiry.get_by_id(int(query))
        except:
          pass
        total = 0
        if p != None and (p.user == self.user):
          total = 1
          iqs=[p]
      else:
        logging.debug('>>> Inquiry.all() <<< [UDB]' + str( self.view.user_db_id.key().id()))
        p = Inquiry.all()
        p.filter(" user_db_id = ",self.view.user_db_id)
        for f in add_filters:
          if f['name'].startswith('iq_'): 
            # "iq_{name} => {name}
            name = f['name'][3:]
            p.filter(name + " = ",f['val'])
            logging.debug('>>> add filter <<< name = ' + f['val'])
        iqs = p.fetch(lines,offset)

      is_id_sort = False
      if sortname != 'id' and sortname != '-id' :
        if sortorder.upper() == 'DESC':
          sortname = '-' + sortname
        p.order(sortname)
      else:
        is_id_sort = True

      logging.debug(">>> p.count() is " + str(p.count()) + " <<<")

      # Profile の絞り込み項目で
      results = []
      for iq in iqs:
        is_added = True
        for f in add_filters:
          # Profile での絞り込みがあった！ 
          if not f['name'].startswith('iq_'): 
            pval = getattr(iq.profile(),f['name'])
            if pval != f['val']:
              is_added = False
        if is_added:
          results.append(iq) 

      if is_id_sort and (sortorder != None and sortorder.upper() == 'DESC'):
        results.reverse()

      config = []
      for col in self.config:
        if col['name'].startswith('iq_') and col['checked'] == 'checked':
          config.append(col)
          continue
        if col['name'] == 'email':
          config.append(col)
          continue
        if col['checked'] == 'checked':
          config.append(col)
   
      rows = []
      total = len(results)
      for rec in results:
        wk = {'id':rec.key().id(),"cell":[rec.key().id()]}
        for col in config:
          val = None
          clazz = None
          name = None
          if col['name'].startswith('iq_'): 
            # "iq_{name} => {name}
            name = col['name'][3:]
            val = getattr(rec,name)
            clazz = Inquiry
          else:
            name = col['name']
            val = getattr(rec.profile(),name)
            clazz = ProfileCore

          if col['type'] == 'radio' or col['type'] == 'select':
            udm = db.GqlQuery("SELECT  * FROM UserDbMaster WHERE name = :1",col['name']).get()
            for item in yaml.load(udm.yaml_data):
              if item['code'] == val:
                val = item['name']

          if isinstance(getattr(clazz,name),db.DateTimeProperty):
            logging.debug(">>> BINGO <<< name is " + col['name'] + " val is " + str(val))
            wk2 = val + datetime.timedelta(hours=9)
            if 'format' in col:
              val = wk2.strftime(col['format'])
              #val = wk2.strftime('%Y/%m/%d')
            else:
              val = wk2.strftime('%Y/%m/%d %H:%M:%S')

          wk['cell'].append(val)

        rows.append(wk)

      data = {'page':page, 'total': total, 'rows': rows }
      self.render(json=self.to_json(data))
