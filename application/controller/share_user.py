#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.share_user import ShareUser
from model.view import UserView

import copy
import yaml

class Share_userController(BaseController):

  def create(self):

    id = self.params.get('shared_view_id')
    view = UserView.get_by_id(int(id))

    config = copy.deepcopy(ShareUser.default_config)

    for col in config:
      key = col['name']
      val = self.params.get(key)
      if val == 'yes':
        col['val']= True
      else:
        col['val']= False

    yaml_data = yaml.dump(config)

    wk = self.params.get('share_users')
    # 改行で分解
    for email in wk.split("\n"):
      ShareUser(share_view_id = view,email = email,config = yaml_data).put()

    res = {'status':'success'}
    self.render(json=self.to_json(res))
