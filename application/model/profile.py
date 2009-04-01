#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel
from model.user_db import UserDb

'''
'''
class ProfileCore(BaseModel):
  claimed_id      = db.StringProperty()
  user_db_id      = db.ReferenceProperty(UserDb)

  email           = db.StringProperty(default='')
  organization    = db.StringProperty(default='')
  last_name       = db.StringProperty(default='')
  first_name      = db.StringProperty(default='')
  name            = db.StringProperty(default='')
  last_name_yomi  = db.StringProperty(default='')
  first_name_yomi = db.StringProperty(default='')
  name_yomi       = db.StringProperty(default='')
  title           = db.StringProperty(default='')
  birthday        = db.IntegerProperty() 
  sex             = db.StringProperty(default='')
  mobile_email     = db.StringProperty(default='')
  zip_code        = db.StringProperty(default='')
  prefecture_code = db.StringProperty(default='')
  city            = db.StringProperty(default='')
  address         = db.StringProperty(default='')
  section         = db.StringProperty(default='')
  tel_no          = db.StringProperty(default='')
  fax_no          = db.StringProperty(default='')
  cellphone_no    = db.StringProperty(default='')
  data            = db.TextProperty(default='')

  disp_columns = [
	{'name':'name','label':'氏名'}
	,{'name':'name_yomi','label':'氏名(かな)'}
	,{'name':'organization','label':'企業/団体'}
	,{'name':'section','label':'所属/部署'}
	,{'name':'title','label':'役職'}
	,{'name':'birthday','label':'生年月日'}
	,{'name':'sex','label':'性別'}
	,{'name':'zip_code','label':'郵便番号'}
	,{'name':'prefecture_code','label':'都道府県'}
	,{'name':'city','label':'市町村区'}
	,{'name':'address','label':'それ以降の住所'}
	,{'name':'email','label':'電子メール'}
	,{'name':'mobile_email','label':'電子メール(携帯)'}
	,{'name':'tel_no','label':'電話番号'}
	,{'name':'cellphone_no','label':'電話番号(携帯)'}
	,{'name':'fax_no','label':'FAX番号'}
  ]

class ProfileEx(BaseModel):
  pass
