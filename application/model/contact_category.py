from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class ContactCategory(BaseModel):
  name = db.StringProperty()
  person_email = db.StringProperty()
  order = db.IntegerProperty()
