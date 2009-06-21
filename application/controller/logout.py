#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController

from google.appengine.api import users
from google.appengine.ext import db

class LogoutController(BaseController):
    def index(self):
      self.redirect(users.create_logout_url("/"))
