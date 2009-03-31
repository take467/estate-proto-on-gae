from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class ProfileGroup(BaseModel):
  user  = db.UserProperty(required=True)
  name  = db.StringProperty(required=True)
  pass
