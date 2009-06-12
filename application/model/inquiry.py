#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.user_db import UserDb
from model.profile import ProfileCore

import yaml

class Inquiry(BaseModel):
  user_db_id     = db.ReferenceProperty(UserDb)
  profile_id     = db.ReferenceProperty(ProfileCore)

  post_at     = db.DateTimeProperty(auto_now_add=True)
  status      = db.StringProperty(default='unanswered')
  title       = db.StringProperty(default=u'お問い合せ(無題)')

  reference_id  = db.StringProperty(default="")
  content     = db.TextProperty(default='')
  reply_content  = db.TextProperty(default='')
  reply_person   = db.StringProperty(default='')
  is_replied     = db.BooleanProperty(default=False)
  reply_at     = db.DateTimeProperty()

  config = db.TextProperty()
  disp_columns = [
      {'name':'iq_reference_id','label':u'お問い合せ番号','width':'100','align':'left','type':'text','search_refinement':False,'hidden':'false','form':'must','checked':'','comment':'以前からのお問い合わせの場合は、お問い合わせ番号を入力してください'}
      ,{'name':'iq_status','label':u'ステータス','checked':'checked','width':'80','align':'left','type':'select','search_refinement':True,'hidden':'false','form':'discard'}
      ,{'name':'iq_post_at','label':u'問い合せ日','checked':'checked','width':'100','align':'left','type':'date','format':'%Y/%m/%d','search_refinement':'false','hidden':'false','form':'discard'}
      ,{'name':'iq_title','label':u'件名','checked':'checked','width':'180','align':'left','type':'text','search_refinement':'false','hidden':'false','form':'must'}
  ]

  def user_db(self):
    return self.user_db_id

  def profile(self):
    return self.profile_id


  def getProperty(self,key):
    prop =  yaml.load(self.config)
    if key in prop:
      return prop.get(key) 
    else:
      return None

  def setProperty(self,key,val):
    prop =  yaml.load(self.config)
    prop[key] = val
    self.config = yaml.dump(prop)


