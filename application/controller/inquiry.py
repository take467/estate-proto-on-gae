#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from google.appengine.api import users
from model.inquiry import *
from model.notice_mail import *

import re
import cgi
from datetime import datetime


class InquiryController(BaseController):
    def before_action(self):
      self.config = InquiryConfig.all().get()
      if self.config == None:
        self.config = InquiryConfig()
	self.config.lead = ""
	self.config.after_word = ""
        self.config.put()

    def delete_category(self):
      idx = self.params.get("idx");

      # カテゴリに属するドキュメントがあったら削除できない
      res= {"status":"success","msg":"削除しました"}
      key= self.config.categories[int(idx)-1]
      c = ContactCategory.get(key)
      c.delete() 
      del self.config.categories[int(idx)-1]
      self.config.put()

      self.render(json=self.to_json(res))


    def doc(self):
        pass

    def edit(self):
        pass

    def index(self):
      try:
        is_replied = self.params['is_replied']
      except:
        is_replied = ''

      if is_replied == 'false':
        #self.inquiries = db.GqlQuery('SELECT * FROM Inquiry WHERE is_replied = :1 ORDER BY is_replied,post_at DESC',False)
        self.inquiries = Inquiry.all().filter('is_replied =',False).order('-post_at')
      else:
        self.inquiries = Inquiry.all().order('-post_at')
      default_c = ContactCategory().all().filter('order=',-1).get()
      if default_c == None:
        default_c = ContactCategory()
        default_c.order=-1
        default_c.name = u"なし"
        default_c.put()
      for inquiry in self.inquiries:
        try:
          if inquiry.category == None:
            inquiry.category = default_c
            inquiry.put()
        except:
          inquiry.category = default_c
          inquiry.put()
        

    def show_by_id(self):
      if self.request.method.upper() == "GET":
        id = int(self.params['id'])
        self.inquiry = Inquiry.get_by_id(id)
        self.form_fields  = []
        for key in self.inquiry.form_fields:
          ff = FormField.get(key)
          self.form_fields.append(ff)
        self.content = re.sub("\n","<br/>",cgi.escape(self.inquiry.content))
        self.render(template="show")

    def show(self):
      if self.request.method.upper() == "GET":
        key = self.params['id']
        self.inquiry = Inquiry.get(key)
        self.form_fields  = []
        for key in self.inquiry.form_fields:
          ff = FormField.get(key)
          self.form_fields.append(ff)
        self.content = re.sub("\n","<br/>",cgi.escape(self.inquiry.content))

      elif self.request.method.upper() == "POST":
        key=self.params['key']
        mode = self.params['mode']
        inquiry = Inquiry.get(key)
        if inquiry:
          if mode == 'edit':
            inquiry.status='redo'
            inquiry.put()
          elif mode == 'send':
            if inquiry.is_replied != True:
              m = NoticeMail()
              m.send_reply(self.request,inquiry)
              inquiry.reply_at = datetime.now()
              inquiry.is_replied = True
              inquiry.status = 'sent'
              inquiry.put()

        self.redirect('/inquiry/show/' + key)

    def setting(self):
     if self.request.method.upper() == "GET":
       # categoris
       self.categories = []
       for key in self.config.categories:
         category = ContactCategory.get(key)
         self.categories.append(category)

       self.category_num = len(self.categories)

       # form_fields
       wk = ""
       try:
         for key in self.config.form_fields:
           f = FormField.get(key)
           if f:
             wk = wk + f.label+"\n"
       except KeyError ,ex:
         pass
       self.fields = wk

     if self.request.method.upper() == "POST":
        self.config.lead = self.params['lead']
        self.config.after_word = self.params['after_word']
        self.config.default_to = self.params['default_to']
       
        # かてごり
        #既存のリスト項目をテーブルから削除
        for key in self.config.categories:
          cc = ContactCategory.get(key) 
          if cc:
            cc.delete()
        self.config.categories = []

        num = 1
        max = 1
        while num <= int(self.params['category_count']):
          name = self.params.get("name%s" % num)
          email = self.params.get("person_email%s" % num)
          if email == None or email == "":
            email = self.config.default_to
          category = ContactCategory(name=name,person_email=email,order=int(num))
          category.put()
          self.config.categories.append(category.key())
          num = num +1
          max = max + 1

        new = self.params['new_category']
        if new:
          email = self.params['new_category_email']
          if email == None or email == "":
            email =  self.config.default_to
          category = ContactCategory(name=new, person_email=email,order=max)
          category.put()
          self.config.categories.append(category.key())

        # 問い合わせ項目
        fields = self.params['fields']
        if fields:
          #既存のform_fieldをテーブルから削除
          for key in self.config.form_fields:
            ff = FormField.get(key)
            if ff:
              ff.delete()
          self.config.form_fields = []

          # line separate
          lines = fields.splitlines()
          num = 1
          for line in lines:
            cf = FormField(label = line,order = num)
            cf.put()
            self.config.form_fields.append(cf.key())
            num = num +1

        self.config.put()

        self.redirect('/inquiry/setting')

    def update(self):
      if self.request.method == "POST":
        key = self.params['id']
        reply_content = self.params['reply_content']
        inquiry = Inquiry.get(key)
        if inquiry:
          inquiry.reply_content = reply_content
          inquiry.status = "draft"
          inquiry.put()

        self.redirect('/inquiry/show/' + key)
