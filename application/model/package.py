from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class Package(BaseModel):
  code    = db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  post_at = db.DateTimeProperty(auto_now_add=True)
