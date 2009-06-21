#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import memcache


from gaeo.controller import BaseController
from model.user_db import *
from model.inquiry import *

import re
import cgi
import copy
import yaml
import datetime

class ContactController(BaseController):
    def before_action(self):
      # かならずURLの最後にはUserDbのIDが付与される
      self.udb = None
      try:
        self.udb = UserDb.get(self.params.get('id'))
      except Exception, ex:
        self.error(400,'Bad Request')
        return

      self.config = yaml.load(self.udb.config)
      self.css = ''
      if  'css' in self.config: 
        self.css =  self.config['css']
      self.form_config = self.config['form_config']

      self.server_name = self.request.environ['SERVER_NAME']
      self.server_port = int(self.request.environ['SERVER_PORT'])
      if self.server_port == 80:
        self.base_url = 'http://%s/' % (self.server_name,)
        self.base_url_nossl = self.base_url
      elif self.server_port == 443:
        self.base_url = 'https://%s/' % (self.server_name,)
        self.base_url_nossl = 'http://%s/' % (self.server_name,)
      else:
        self.base_url = ('http://%s:%s/' % (self.server_name, self.server_port))
        self.base_url_nossl = self.base_url

    def preview(self):
      self.w = self.params.get('w','700')
      self.h = self.params.get('h','550')
      pass

    def confirm(self):

      self.ticket = self.params.get('ticket','')
      self.session_val = self.params.get('session_val','')
      if self.ticket and db.GqlQuery("SELECT * FROM Inquiry WHERE ticket = :1",self.ticket).get():
        self.redirect('/contact/form/'+str(self.udb.key()))
        return

      self.action_url = self.base_url + "contact/post/" + str(self.udb.key())

      # FORM FIELD の更新
      self.form_fields = []
      #self.form_config = self.udb.getProperty('form_config')
      for col in self.form_config:
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):

          #col['val'] = re.sub("\n","<br/>",cgi.escape(self.params.get(col['name'])))
          col['val'] = self.params.get(col['name'])

          if col['type'] == 'radio' or col['type'] == 'select':
            result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
            if result.count() > 0:
              rec = result.get()
              for item in yaml.load(rec.yaml_data):
                if item['code'] == col['val']:
                  col['code'] = item['code']
                  col['val'] = item['name']
          self.form_fields.append(col)


    def form(self):
      self.action_url = self.base_url + "contact/confirm/" + str(self.udb.key())
      start_over = False

      self.ticket = self.params.get('ticket','')
      self.session_val = self.params.get('session_val','')

      # CSRF対策 
      if not self.ticket:
        import md5
        m=md5.new()
        self.ticket = str(m)
        m.update(self.ticket + str(self.udb.key()))
        self.session_val = m.hexdigest()

        # cookieが使えないことも考慮してmemcacheに値をいれる
        memcache.add(key=self.ticket,value=self.session_val)

      else:
        if db.GqlQuery("SELECT * FROM Inquiry WHERE ticket = :1",self.ticket).get():
          self.redirect('/contact/form/'+str(self.udb.key()))
          return

      if self.request.method.upper() == "POST":
        start_over = True

      self.fields = []
      for col in self.form_config:
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):
          if start_over:
            col['val']  = self.params.get(col['name'])
            if col['type'] == 'textarea':
               col['val'] = self.params.get(col['name'])
               #s = re.sub("<br/>","\n",self.params.get(col['name']))
               #s = s.replace("&amp;", "&") # Must be done first!
               #s = s.replace("&lt;","<")
               #s = s.replace("&gt;",">")
               #s = s.replace("&quot;",'"')
               #col['val'] = s
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

          # darty hack
          if col['name'] == 'email':
            wk = copy.deepcopy(col)
            wk['name'] = 'email_confirm'
            wk['label'] = '電子メール（確認)'
            wk['comment'] = None
            wk['validator'] = "Validator.check(this,'equal','email')"
            self.fields.append(wk)


    # 問い合わせを保存
    def post(self):
      # チケットの確認
      ticket  = self.params.get('ticket')
      session_val = self.params.get('session_val')

      if db.GqlQuery("SELECT * FROM Inquiry WHERE ticket = :1",ticket).get():
        self.redirect('/contact/form/'+str(self.udb.key()))
        return

      wk = memcache.get(ticket)
      try:
        if wk == None or (session_val != wk):
          self.redirect('/contact/form/'+str(self.udb.key()))
	  return
      except:
        self.redirect('/contact/form/'+str(self.udb.key()))
	return


      profile = ProfileCore(user_db_id = self.udb,user=self.udb.user)
      profile.put()
      inquiry = Inquiry(user_db_id = self.udb,profile_id = profile,ticket=ticket)
      # FORM FIELD の更新
      #self.form_config =  self.udb.getProperty('form_config')
      for col in self.form_config:
        #if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):

        name = col['name']
        val =self.params.get(name,'None')
        if val != 'None':
          if name.startswith('iq_'):
            name = name[3:]
            setattr(inquiry,name,val)
          else:
            setattr(inquiry.profile(),name,val)

      inquiry.profile().put()
      inquiry.put() 
      self.inquiry = inquiry

      # FORM FIELD の更新
      self.form_fields = []
      for col in self.form_config:
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):
          #col['val'] = re.sub("\n","<br/>",cgi.escape(self.params.get(col['name'])))
          col['val'] = self.params.get(col['name'])
          if col['type'] == 'radio' or col['type'] == 'select':
            result = db.GqlQuery("SELECT * FROM UserDbMaster WHERE name = :1",col['name'])
            if result.count() > 0:
              rec = result.get()
              for item in yaml.load(rec.yaml_data):
                if item['code'] == col['val']:
                  col['code'] = item['code']
                  col['val'] = item['name']
          self.form_fields.append(col)

      # 担当者にメールを送る
      email = inquiry.user_db().getProperty('recipients')
      values = {'email':email,'id':inquiry.key().id(),'db_name':inquiry.user_db().name}

      subject = self.render_txt(template="notice_mail_subject",values=values)
      body    = self.render_txt(template="notice_mail_body",values=values)

      if mail.is_email_valid(email):
          mail.send_mail(sender=email, to=email, subject=subject, body=body)

      # /user_db/config/edit/ /user_db/config/update のほうがわかりやすいかURLマッピング
      # 問い合わせした人にメールを送る
      name = inquiry.profile().email
      if inquiry.profile().name:
        name = inquiry.profile().name
      values = {'name':name,'id':inquiry.key().id(),'db_name':inquiry.user_db().name}

      # SUBJECT
      subject = '{{id}}'
      ts = self.udb.getProperty('confirm_mail_subject')
      if ts:
        subject = self.render_txt(template_string=ts,values=values)
      else:
        subject = self.render_txt(template="confirm_mail_subject",values=values)

      # BODY
      body = ''
      ts = self.udb.getProperty('confirm_mail_body')
      if ts:
        body = self.render_txt(template_string=ts,values=values)
      else:
        body = self.render_txt(template="confirm_mail_body",values=values)

      if mail.is_email_valid(inquiry.profile().email):
          mail.send_mail(sender=email, to=inquiry.profile().email, subject=subject, body=body)

      try:
        memcache.delete(ticket)
      except KeyError ,ex:
        self.render(text=ex) 
        return
