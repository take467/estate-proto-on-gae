#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController

from model.site import Site
from model.category import Category
from model.document import Document
from model.genre import Genre
from model.package import Package
from model.product import Product
from model.page import Page

class SiteController(BaseController):

    def before_action(self):
      sites = Site.all()
      count = sites.count()
      if count > 1:
        for s in sites:
          s.delete()
        count = 0

      if count == 0:
        logo_label = "Verona"
        logo_subtext = u"健康deネット- IT事業部"
        description = u"健康deねっとではIT事業を行っています。"
        keywords =u"Ruby On Rails,RoR,個人情報保護,google app engine,GAE"
        self.site = Site(logo_label=logo_label,logo_subtext=logo_subtext,description=description,keywords=keywords,g_navi_categories=[],b_navi_categories = [])
        self.site.put()
      elif count == 1:
        self.site = sites.get() 


    def bottom_navi(self):
      item_order = [1,2,3,4]
      if self.request.method.upper() == "GET":
        self.categories = Category.all().order('-post_at')
        self.item_order = item_order

      #保存
      if self.request.method.upper() == "POST":
        self.site.b_navi_categories = []
        for i in item_order:
          name = "bottom_menu%d" % i
          key = self.params.get(name)
          if key != None and key != "":
            c = Category.get(key)
            if c:
              self.site.b_navi_categories.append(c.key())
        self.site.put()
        self.redirect('/site/bottom_navi')

    def global_navi(self):
      item_order = [1,2,3,4,5]
      if self.request.method.upper() == "GET":
        self.categories = Category.all().order('-post_at')
        self.item_order = item_order

      #保存
      if self.request.method.upper() == "POST":
        self.site.g_navi_categories = []
        for i in item_order:
          name = "global_menu%d" % i
          key = self.params.get(name)
          if key != None and key != "":
            c = Category.get(key)
            if c:
              self.site.g_navi_categories.append(c.key())
        self.site.put()
        self.redirect('/site/global_navi')
    

    def category(self):
        query = Category.all()
        query.order('-post_at')
        self.result = query

    def genre(self):
        query = Genre.all()
        query.order('-post_at')
        self.result = query

    def package(self):
        query = Package.all()
        query.order('-post_at')
        self.result = query

    def document(self):

        query = Category.all()
        query.order('-post_at')
        self.categories = query

        query = Document.all()
        self.result = query

    def page(self):

        query = Page.all()
        self.result = query


    def edit(self):
      self.rec =  self.site

    def index(self):
        self.rec = Site.all().get()
        if self.rec == None:
          self.redirect('/site/edit')

    def update(self):
        site = Site.get(self.params.get('key'))
        site.logo_label = self.params.get('logo_label')
        site.logo_subtext = self.params.get('logo_subtext')
        site.description  = self.params.get('description')
        site.keywords = self.params.get('keywords')
        site.content = self.params.get('content')
        site.sidebar_label = self.params.get('sidebar_label')
        site.sidebar_content = self.params.get('sidebar_content')
        site.put()

        self.redirect('/site/edit')

    def profile(self):
      pass
    def product(self):
      #self.products = Product.all()
      self.genres = Genre.all()
      self.packages = Package.all()

