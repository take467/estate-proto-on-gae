#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.controller import BaseController

from model.site import Site
from model.category import Category
from model.document import Document
from model.profile import Profile
from model.package import Package
from model.product import Product
from model.attribute import Attribute
from google.appengine.api import users
from django.core.paginator import ObjectPaginator, InvalidPage

class ShowcaseController(BaseController):
    def before_action(self):
      self.logged_in = True
      self.claimed_id = None
      try:
        self.claimed_id = self.cookies['claimed_id']
        if self.claimed_id == None or self.claimed_id == '':
          self.logged_in = False
      except:
        self.logged_in = False

      #self.user = users.get_current_user()
      #if self.user:

      self.url = "/logout"
      self.url_text = 'ログアウト'
      self.profile = db.GqlQuery("SELECT * FROM Profile WHERE claimed_id = :1",self.claimed_id).get()

      #else:
      #  self.url = users.create_login_url(self.request.url)
      #  self.url_text = 'ログイン'
      pass

    def index(self):
      if not self.logged_in:
        self.redirect("/login")
        return

      results = db.GqlQuery("SELECT * FROM Attribute WHERE profile = :1 and name = :2",self.profile,'purchased_package')
      self.packages = []
      genre_hash = {}
      self.genres = []
      for a in results:
        p = db.GqlQuery("SELECT * FROM Package WHERE code = :1",a.val).get()
        self.packages.append(p)

        results2 = db.GqlQuery("SELECT * FROM Product WHERE package_code = :1",a.val)
        for product in results2:
          genre = db.GqlQuery("SELECT *FROM Genre WHERE genre_code = :1",product.genre_code).get()
          if genre:
            genre_hash[product.genre_code] = genre

      for key, value in genre_hash.iteritems():
	self.genres.append(value)

      # product リスト
      products = []
      p_code = self.params.get('p')
      g_code = self.params.get('g')
      if p_code:
        wk = db.GqlQuery("SELECT * FROM Package WHERE code = :1",p_code).get()
        self.bread_clumbs = wk.name
        results = db.GqlQuery("SELECT * FROM Product WHERE package_code = :1 ",p_code)
        products.extend(results)
      else:
        for p in self.packages:
          results = None
          if g_code:
            wk = db.GqlQuery("SELECT * FROM Genre WHERE genre_code = :1",g_code).get()
            self.bread_clumbs = wk.name
            results = db.GqlQuery("SELECT * FROM Product WHERE package_code = :1 and genre_code = :2",p.code,g_code)
          else:
            results = db.GqlQuery("SELECT * FROM Product WHERE package_code = :1 ",p.code)

          if results != None:
            products.extend(results)

      #paginator = ObjectPaginator(products,10)
      #page = int(self.params.get('page',0))
      self.products = products

      #self.is_paginated = True
      #self.products_per_page = 10
      #self.has_next =  paginator.has_next_page(page)
      #self.has_previous = paginator.has_previous_page(page)
      #self.page =  page + 1
      #self.next =  page + 1
      #self.previous =  page -1
      #self.pages = paginator.pages
      
    def sample2(self):
      pass
