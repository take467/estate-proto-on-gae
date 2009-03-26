from google.appengine.ext import db

from gaeo.controller import BaseController
from model.site import Site


class SearchController(BaseController):
  def index(self):

    self.site = Site.all().get()
    pass
