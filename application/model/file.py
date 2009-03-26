from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

import jst
import urllib

class File(BaseModel):
  filename = db.StringProperty()
  orginal_filename = db.StringProperty()
  content_type = db.StringProperty(default='application/octet-stream')
  body = db.BlobProperty()
  content_length =db.IntegerProperty()
  uploaded_at = db.DateTimeProperty(auto_now_add = True)
 
  def quoted_filename(self):
    return urllib.quote(self.filename.encode('utf-8'))
