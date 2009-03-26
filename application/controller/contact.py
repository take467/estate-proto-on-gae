#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.site import Site
from model.category import Category
from model.inquiry import *
from model.notice_mail import *

import re
import cgi

class ContactController(BaseController):
    def before_action(self):
      self.site = Site.all().get()
      self.config = InquiryConfig.all().get()
      if self.config == None:
        self.config = InquiryConfig()
        self.config.put()

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


    def index(self):
      # チケットの発行
      self.session['ticket'] = self.config.key()
      self.session.put()


      if self.config.categories and len(self.config.categories) > 0:
        self.contact_categories = []
        for key in self.config.categories:
          cc = ContactCategory.get(key)
          self.contact_categories.append(cc)

      selected = None
      inquiry = None
      try:
        inquiry = self.session['inquiry']
        if inquiry:
          selected = inquiry.category
      except KeyError ,ex:
        pass

      self.inquiry = inquiry
      self.item_num = 0
      self.fields = []
      if inquiry:
        self.form_fields = self.session['form_fields']
      else:
        self.form_fields=[]
        for key in self.config.form_fields:
          wk = FormField.get(key)
          if wk:
            wk.val = ""
            self.form_fields.append(wk)
            self.item_num = self.item_num + 1

      #if self.inquiry.category == None:
      #  self.inquiry.category = ContactCategory()
      #  self.inquiry.category.name = "なし"


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
