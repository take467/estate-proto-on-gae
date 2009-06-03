#!-*- coding:utf-8 -*-
from model.user_db import *
import yaml

w = UserDbMaster.all()
if w.count() == 0:
 status = [
	{'code':'active','name':u'有効'}
	,{'code':'expired','name':u'無効'}
 ]
 iq_status = [
	{'code':'unanswered','name':u'未回答'}
	,{'code':'answered','name':u'回答'}
]
 sex = [
	{'code':'male','name':u'男性'},
	{'code':'female','name':u'女性'}
 ]

 prefecture = [
  {'code':'01','name':u'北海道'},
  {'code':'02','name':u'青森県'},
  {'code':'03','name':u'岩手県'},
  {'code':'04','name':u'宮城県'},
  {'code':'05','name':u'秋田県'},
  {'code':'06','name':u'山形県'},
  {'code':'07','name':u'福島県'},
  {'code':'08','name':u'茨城県'},
  {'code':'09','name':u'栃木県'},
  {'code':'10','name':u'群馬県'},
  {'code':'11','name':u'埼玉県'},
  {'code':'12','name':u'千葉県'},
  {'code':'13','name':u'東京都'},
  {'code':'14','name':u'神奈川県'},
  {'code':'15','name':u'新潟県'},
  {'code':'16','name':u'富山県'},
  {'code':'17','name':u'石川県'},
  {'code':'18','name':u'福井県'},
  {'code':'19','name':u'山梨県'},
  {'code':'20','name':u'長野県'},
  {'code':'21','name':u'岐阜県'},
  {'code':'22','name':u'静岡県'},
  {'code':'23','name':u'愛知県'},
  {'code':'24','name':u'三重県'},
  {'code':'25','name':u'滋賀県'},
  {'code':'26','name':u'京都府'},
  {'code':'27','name':u'大阪府'},
  {'code':'28','name':u'兵庫県'},
  {'code':'29','name':u'奈良県'},
  {'code':'30','name':u'和歌山県'},
  {'code':'31','name':u'鳥取県'},
  {'code':'32','name':u'島根県'},
  {'code':'33','name':u'岡山県'},
  {'code':'34','name':u'広島県'},
  {'code':'35','name':u'山口県'},
  {'code':'36','name':u'徳島県'},
  {'code':'37','name':u'香川県'},
  {'code':'38','name':u'愛媛県'},
  {'code':'39','name':u'高知県'},
  {'code':'40','name':u'福岡県'},
  {'code':'41','name':u'佐賀県'},
  {'code':'42','name':u'長崎県'},
  {'code':'43','name':u'熊本県'},
  {'code':'44','name':u'大分県'},
  {'code':'45','name':u'宮崎県'},
  {'code':'46','name':u'鹿児島県'},
  {'code':'47','name':u'沖縄県'}
 ]

 UserDbMaster(name='sex',yaml_data=yaml.dump(sex)).put()
 UserDbMaster(name='prefecture',yaml_data=yaml.dump(prefecture)).put()
 UserDbMaster(name='status',yaml_data=yaml.dump(status)).put()
 UserDbMaster(name='iq_status',yaml_data=yaml.dump(iq_status)).put()
