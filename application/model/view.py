#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel

from model.user_db import UserDb
from model.profile import *
from model.inquiry import *
import yaml
import copy

class UserView(BaseModel):
  user_db_id     = db.ReferenceProperty(UserDb)
  name   = db.StringProperty(default=u'新規ビュー')
  config = db.TextProperty()

  def user_db(self):
    return self.user_db_id

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

  @classmethod
  def newInstance(cls,udb,):
    # ついでにビューもつくってしまう
    cols = None
    if udb.service_type == 'c':
      # 問い合わせフォーム専用ビュー
      cols = cls.__set_inquiry_cols()
    else:
      cols = copy.deepcopy(ProfileCore.disp_columns)

    v = UserView(user_db_id = udb,config=yaml.dump(cols))
    v.put()
    id= v.key().id()
    v.name=u'ビュー('+str(id)+')'
    v.put()
    return v


  @classmethod
  def __set_inquiry_cols(cls): 

    # Inquiryの表示情報がメイン
    cols = [{'name':'iq_reference_id','label':u'お問い合わせ番号','width':'80','align':'left','type':'text','search_refinement':False,'hidden':'false','form':'must','checked':'','comment':'以前からのお問い合わせの場合は、お問い合わせ番号を入力してください'}]
    cols.extend(copy.deepcopy(Inquiry.disp_columns))
    #送信者(E-Mail)
    for col in ProfileCore.disp_columns:
      wk = copy.copy(col)
      if wk['name'] == 'status' or wk['name'] == 'post_at':
        wk['form'] = 'discard'
        wk['checked'] = ''
      elif wk['name'] == 'email':
        wk['form'] = 'must'
        wk['comment'] = '最後に確認のメールをお送りしますので正確に入力してください'
      else:
        wk['form'] = 'option'
        wk['checked'] = ''
      cols.append(wk)

    return cols
