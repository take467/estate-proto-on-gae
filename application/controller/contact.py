#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.user_db import *
from model.inquiry import *
from model.notice_mail import *

import re
import cgi

class ContactController(BaseController):
    def before_action(self):
      self.server_name = self.request.environ['SERVER_NAME']
      self.server_port = int(self.request.environ['SERVER_PORT'])
      if self.server_port != 80:
        self.base_url = ('http://%s:%s/' % (self.server_name, self.server_port))
      else:
        self.base_url = 'http://%s/' % (self.server_name,)

    def confirm(self):
      # チケットの確認
      try:
        ticket = self.session['ticket']
        if ticket == None:
          self.redirect('/contact')
          return
      except:
        self.redirect('/contact')
        return

      self.inquiry = Inquiry()

      #お問い合わせ番号
      self.inquiry.reference_id = self.params['inquiry_id']

      # カテゴリ
      try:
        key = self.config.categories[int(self.params['category_order']) -1]
        category = ContactCategory.get(key)
        self.inquiry.category = category
        self.inquiry.to       = category.person_email
      except KeyError ,ex:
        self.inquiry.to       = self.config.default_to

      # メールアドレス
      self.inquiry.from_email = self.params['from']

      # FORM FIELD の更新
      max  = int(self.params['item_num'])
      num = 1
      self.form_fields = []
      while num <= max:
        field = FormField(val=self.params["val%s" % num],label=self.params["label%s" % num],order=num)
        self.form_fields.append(field)
	num = num + 1

      self.form_fields_num = len(self.form_fields)

      # 問い合わせ内容
      self.inquiry.content  = self.params['content']
      self.content = re.sub("\n","<br/>",cgi.escape(self.inquiry.content))

      self.session['inquiry'] = self.inquiry
      self.session['form_fields'] = self.form_fields
      self.session.put()


    def preview(self):
      # チケットの発行
      self.udb = UserDb.get_by_id(int(self.params.get('id')))

      self.session['ticket'] = str(self.udb.key())
      self.session.put()



    def form(self):
      self.udb = UserDb.get_by_id(int(self.params.get('id')))
      self.action_url = "/contact/confirm"

      self.fields = []
      self.form_config = self.udb.getProperty('form_config')
      for col in self.form_config:
        if col['form'] == 'must' or ( col['form'] != 'discard' and col['checked'] == 'checked'):
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
      self.render(template="form")






    def post(self):
      # チケットの確認
      try:
        ticket = self.session['ticket']
        if ticket == None:
          self.redirect('/contact')
	  return
      except:
        self.redirect('/contact')
	return

      try:
        inquiry = self.session['inquiry']
        form_fields = self.session['form_fields']
        self.session['inquiry']=None
        self.session['form_fields']=None
        self.session['ticket']=None
        del self.session['inquiry']
        del self.session['form_fields']
        del self.session['ticket']
        self.session.put()
        for ff in form_fields:
          ff.put()
          inquiry.form_fields.append(ff.key())

        inquiry.put() 

        # ここで person_toとfrom_toにメールを送る
        m = NoticeMail()
        m.notice(self.request,inquiry)
        m.send_confirm(self.request,inquiry)

        self.redirect('/contact/sent')

      except KeyError ,ex:
        self.render(text=ex) 

    def sent(self):
      pass
