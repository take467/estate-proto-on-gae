#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController

from model.site import Site
from model.category import Category
from model.document import Document
from google.appengine.api import users

class WelcomeController(BaseController):
    def before_action(self):
      pass

    def index(self):
      pass
