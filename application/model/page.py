from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.document import Document

class Page(BaseModel):
  name = db.StringProperty(required=True)
  content = db.TextProperty()
  description = db.TextProperty()
  document = db.ReferenceProperty(Document)
  post_at = db.DateTimeProperty(auto_now_add=True)
  order = db.IntegerProperty()
