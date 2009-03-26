from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.profile import Profile


class Attribute(BaseModel):
  profile = db.ReferenceProperty(Profile)
  group   = db.StringProperty()
  label   = db.StringProperty()
  name    = db.StringProperty()
  val     = db.StringProperty()
  attr_id = db.StringProperty()
  config  = db.TextProperty()
