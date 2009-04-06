#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel
from model.user_db import UserDb

class ProfileCore(BaseModel):
  claimed_id      = db.StringProperty()
  user_db_id      = db.ReferenceProperty(UserDb)
  user            = db.UserProperty(required=True)
  email           = db.StringProperty(default='')
  organization    = db.StringProperty(default='')
  last_name       = db.StringProperty(default='')
  first_name      = db.StringProperty(default='')
  name            = db.StringProperty(default='')
  last_name_yomi  = db.StringProperty(default='')
  first_name_yomi = db.StringProperty(default='')
  name_yomi       = db.StringProperty(default='')
  title           = db.StringProperty(default='')
  birthday        = db.StringProperty(default='') 
  sex             = db.StringProperty(default='')
  mobile_email    = db.StringProperty(default='')
  zipcode        = db.StringProperty(default='')
  prefecture      = db.StringProperty(default='')
  city            = db.StringProperty(default='')
  address         = db.StringProperty(default='')
  section         = db.StringProperty(default='')
  tel_no          = db.StringProperty(default='')
  fax_no          = db.StringProperty(default='')
  cellphone_no    = db.StringProperty(default='')
  data            = db.TextProperty(default='')

  disp_columns = [
	{'name':'name','label':'氏名','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
	,{'name':'name_yomi','label':'氏名(かな)','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
	,{'name':'organization','label':'企業/団体','checked':'checked','width':'180','align':'left','type':'text','search_refinement':True}
	,{'name':'section','label':'所属/部署','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
	,{'name':'title','label':'役職','checked':'checked','width':'80','align':'left','type':'text','search_refinement':True}
	,{'name':'birthday','label':'生年月日','checked':'checked','width':'100','align':'left','type':'date','format':'yyyy/mm/dd','search_refinement':False}
	,{'name':'sex','label':'性別','checked':'checked','width':'30','align':'left','type':'radio','search_refinement':True}
	,{'name':'zipcode','label':'郵便番号','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
	,{'name':'prefecture','label':'都道府県','checked':'checked','width':'60','align':'left','type':'select','search_refinement':True}
	,{'name':'city','label':'市町村区','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
	,{'name':'address','label':'それ以降の住所','checked':'checked','width':'180','align':'left','type':'text','search_refinement':False}
	,{'name':'email','label':'電子メール','checked':'checked','width':'120','align':'left','type':'text','search_refinement':False}
	,{'name':'mobile_email','label':'電子メール(携帯)','checked':'checked','width':'120','align':'left','type':'text','search_refinement':False}
	,{'name':'tel_no','label':'電話番号','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
	,{'name':'cellphone_no','label':'電話番号(携帯)','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
	,{'name':'fax_no','label':'FAX番号','checked':'checked','width':'100','align':'left','type':'text','search_refinement':False}
  ]

class ProfileEx(BaseModel):
  pass
