from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel
from model.contact_category import ContactCategory

class FormField(db.Model):
  label = db.StringProperty()
  order = db.IntegerProperty()
  val   = db.StringProperty()
  selected = db.BooleanProperty()

class ContactCategory(BaseModel):
  name = db.StringProperty()
  person_email = db.StringProperty()
  order = db.IntegerProperty()

class Inquiry(BaseModel):
  status      = db.StringProperty(default='unprocessed')
  category    = db.ReferenceProperty(ContactCategory)
  from_email  = db.StringProperty() 
  reference_id  = db.StringProperty(default="")
  to          = db.EmailProperty()
  post_at     = db.DateTimeProperty(auto_now_add=True)
  form_fields = db.ListProperty(db.Key)
  content     = db.TextProperty(default='')
  reply_content  = db.TextProperty(default='')
  is_replied     = db.BooleanProperty(default=False)
  reply_at     = db.DateTimeProperty()


class InquiryConfig(BaseModel):
  lead        = db.TextProperty()
  after_word  = db.TextProperty()
  default_to  = db.EmailProperty()
  categories  = db.ListProperty(db.Key)
  form_fields = db.ListProperty(db.Key)
