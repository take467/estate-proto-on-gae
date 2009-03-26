from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class Document(BaseModel):
  published   = db.BooleanProperty(default=False)
  document_id =  db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  description = db.TextProperty()
  content = db.TextProperty()
  category_id = db.StringProperty(default=None)
  category_name = db.StringProperty()
  post_at = db.DateTimeProperty(auto_now_add=True)

  def category(self):
    return db.GqlQuery("SELECT * FROM Category WHERE category_id = :1 ",self.category_id).get()
