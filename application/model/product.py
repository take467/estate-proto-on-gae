from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel
from model.genre import Genre
from model.package import Package

class Product(BaseModel):
  package_code     = db.StringProperty()
  genre_code = db.StringProperty()
  title = db.StringProperty(default="")
  released_at = db.DateTimeProperty(auto_now_add=True)
  author = db.StringProperty(default="")
  description = db.TextProperty(default="")
  filename = db.StringProperty(default="")
  duration = db.StringProperty(default="")
  thumbnail = db.BlobProperty()
  thumbnail_filename = db.StringProperty()

  def genre(self):
    return db.GqlQuery("SELECT * FROM Genre WHERE genre_code = :1 ",self.genre_code).get()

  def package(self):
    return db.GqlQuery("SELECT * FROM Package WHERE code = :1 ",self.package_code).get()
