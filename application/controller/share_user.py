#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.share_user import ShareUser
from model.view import UserView
from model.notice_mail import *

import copy
import yaml

class Share_userController(BaseController):

  def delete(self):
    id = self.params.get('id')

    res = {'status':'success'}
    su=ShareUser.get_by_id(int(id))
    if su:
      su.delete()
    else:
      res={'status':'error','msg':u"対象のビューが見つかりません(ID:%s)" % id}

    self.render(json=self.to_json(res))

  def create(self):

    id = self.params.get('shared_view_id')
    view = UserView.get_by_id(int(id))

    config = copy.deepcopy(ShareUser.default_config)

    for col in config:
      key = col['name']
      val = self.params.get(key)
      if val == 'yes':
        col['val']= 'true'
      else:
        col['val']= 'false'

    yaml_data = yaml.dump(config)
    wk = self.params.get('share_users')
    # 改行で分解
    email = ''
    try:
      for e  in wk.split("\n"):
        email = e
        res = {'status':'success'}
        su = ShareUser(share_view_id = view,email = email,config = yaml_data)
        # メールで通知する
        m = NoticeMail()
        m.notice_share(self.request,su)
        su.put()
    except:
        res = {'status':'error','msg':u"%sへの共有に失敗しました" % email}

    self.render(json=self.to_json(res))
