from google.appengine.ext import db

from gaeo.controller import BaseController
from google.appengine.api import users


class VeronaController(BaseController):
    def login(self):
      self.redirect(users.create_login_url('/site'))

    def logout(self):
      self.redirect(users.create_logout_url('/site'))
