from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

class Profile(BaseModel):
  claimed_id = db.StringProperty()
  user       = db.UserProperty()
  email      = db.StringProperty(default='')
  organization  = db.StringProperty(default='')
  last_name  = db.StringProperty(default='')
  first_name = db.StringProperty(default='')
  last_name_hira = db.StringProperty(default='')
  first_name_hira = db.StringProperty(default='')
  title           = db.StringProperty(default='')
  birthday = db.IntegerProperty() 
  sex      = db.StringProperty(default='')
  mobil_email = db.StringProperty(default='')
  zip_code    = db.StringProperty(default='')
  prefecture  = db.StringProperty(default='')
  city           = db.StringProperty(default='')
  address        = db.StringProperty(default='')
  section        = db.StringProperty(default='')
  tel_no         = db.StringProperty(default='')
  fax_no         = db.StringProperty(default='')
  cellphone_no   = db.StringProperty(default='')
