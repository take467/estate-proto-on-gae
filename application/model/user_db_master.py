#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.model import BaseModel, SearchableBaseModel
from model.profile import *
from model.inquiry import *

import yaml
import copy

class UserDbMaster(BaseModel):
  name = db.StringProperty(required=True)
  yaml_data = db.TextProperty()

  @classmethod
  def getFormConfig(cls):  

    # Inquiryの表示情報がメイン
    cols = copy.deepcopy(Inquiry.disp_columns)
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

    cols.append({'name':'iq_content','label':u'お問い合わせ内容','cols':'60','rows':'10','type':'textarea','search_refinement':False,'hidden':'false','form':'must','checked':''})

    return cols
