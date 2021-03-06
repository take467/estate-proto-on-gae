#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel
from model.user_db import UserDb
import yaml

class ProfileCore(BaseModel):
  claimed_id      = db.StringProperty()
  user_db_id      = db.ReferenceProperty(UserDb)
  user            = db.UserProperty()
  passwd          = db.StringProperty(default='')
  status          = db.StringProperty(default='active')
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
  zipcode         = db.StringProperty(default='')
  prefecture      = db.StringProperty(default='')
  city            = db.StringProperty(default='')
  address         = db.StringProperty(default='')
  section         = db.StringProperty(default='')
  tel_no          = db.StringProperty(default='')
  fax_no          = db.StringProperty(default='')
  cellphone_no    = db.StringProperty(default='')
  data            = db.TextProperty(default='')
  post_at         = db.DateTimeProperty(auto_now_add=True)


  def getLabel(self,name,code):
    udm = db.GqlQuery("SELECT  * FROM UserDbMaster WHERE name = :1",name).get()
    for item in yaml.load(udm.yaml_data):
      if item['code'] == code:
        val = item['name']
        return val

  disp_columns = [
	{'name':'post_at','label':u'登録日','checked':'checked','width':'80','align':'right','type':'hidden','hidden':'true','format':'%Y/%m/%d %H:%M:%S','search_refinement':'false'}
	,{'name':'status','label':u'ステータス','checked':'checked','width':'80','align':'left','type':'select','search_refinement':True,'hidden':'true'}
	,{'name':'name','label':u'氏名','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'name_yomi','label':u'氏名(かな)','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'organization','label':u'企業/団体','checked':'checked','width':'180','align':'left','type':'text','search_refinement':True,'hidden':'false'}
	,{'name':'section','label':'所属/部署','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'title','label':u'役職','checked':'checked','width':'80','align':'left','type':'text','search_refinement':True,'hidden':'false'}
	,{'name':'birthday','label':u'生年月日','checked':'checked','width':'100','align':'left','type':'date','format':'yyyy/mm/dd','search_refinement':'false','hidden':'false'}
	,{'name':'sex','label':u'性別','checked':'checked','width':'30','align':'left','type':'radio','search_refinement':True,'hidden':'false'}
	,{'name':'zipcode','label':u'郵便番号','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'prefecture','label':u'都道府県','checked':'checked','width':'60','align':'left','type':'select','search_refinement':True,'hidden':'false'}
	,{'name':'city','label':u'市町村区','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'address','label':u'それ以降の住所','checked':'checked','width':'180','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'email','label':u'電子メール','checked':'checked','width':'150','align':'left','type':'text','search_refinement':'false','hidden':'false','form':'must','validator':"Validator.check(this,'mail')"}
	,{'name':'mobile_email','label':u'電子メール(携帯)','checked':'checked','width':'150','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'tel_no','label':u'電話番号','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'cellphone_no','label':u'電話番号(携帯)','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
	,{'name':'fax_no','label':u'FAX番号','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'}
  ]

class ProfileEx(BaseModel):
  pass
