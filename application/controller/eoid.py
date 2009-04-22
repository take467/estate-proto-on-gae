#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users

from gaeo.controller import BaseController
import urllib
import re
import cgi

from openid.consumer import discover


class EoidController(BaseController):
    def before_action(self):
      self.user = users.get_current_user()
      self.server_name = self.request.environ['SERVER_NAME']
      self.server_port = int(self.request.environ['SERVER_PORT'])
      if self.server_port != 80:
        self.base_url = ('http://%s:%s/eoid/' % (self.server_name, self.server_port))
      else:
        self.base_url = 'http://%s/eoid/' % (self.server_name,)
      if self.user:
        self.loginname =  self.user.email()
        self.auth_url = users.create_logout_url("/eoid/login")
        self.auth_url_text = 'ログアウト'
      else:
        self.loginname = '未ログイン'
        self.auth_url = users.create_login_url("/eoid/login")
        self.auth_url_text = 'ログイン'

    def index(self):
      self.x_xrds_location = self.base_url + 'serveryadis'
      if self.user:
        self.openid_url = self.base_url + 'id/?e=' + self.user.email()

    def openidserver(self):
      pass

    def login(self):
      #GET
      if self.request.method.upper() == "GET":

        if self.user:
          # ログイン済みならリダイレクト
          #self.redirect("/eoid/id/" +  re.sub('\.','+',self.user.email()))
          self.redirect("/eoid/id/?e=" + self.user.email())
        else:
          #self.success_to = "/"
          #self.fail_to = "/"
          self.redirect(users.create_login_url("/eoid/login"))

      #POST
      if self.request.method.upper() == "POST":
        pass

    def id(self):
      #self.email = re.sub(' ','.',self.params.get('e'))
      self.email = self.params.get('e')
      #self.email = self.params.get('e')
      self.trust_root = self.base_url
      self.openid_server = self.base_url + "openidserver"
      self.x_xrds_location = self.base_url + 'yadis/?e='+self.email
      self.claimed_id = self.base_url + "id/?e="+ self.email
      pass

    def yadis(self):
        #self.send_response(200)
        #self.send_header('Content-type', 'application/xrds+xml')
        #self.end_headers()

      self.email = self.params.get('e')
      endpoint_url = self.base_url + 'openidserver'
      user_url = self.base_url + 'id/?e-=' + self.email
      buff="""\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type>%s</Type>
      <Type>%s</Type>
      <URI>%s</URI>
      <LocalID>%s</LocalID>
    </Service>

  </XRD>
</xrds:XRDS>
"""%(discover.OPENID_2_0_TYPE, discover.OPENID_1_0_TYPE,
     endpoint_url, user_url)
      self.render(binary=buff,content_type='application/xrds+xml')

    def serveryadis(self):
      endpoint_url = self.base_url + 'openidserver'
      buff="""\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type>%s</Type>
      <URI>%s</URI>
    </Service>

  </XRD>
</xrds:XRDS>
"""%(discover.OPENID_IDP_2_0_TYPE, endpoint_url,)
      self.render(binary=buff,content_type='application/xrds+xml')


    def __writeUserHeader(self):
        if self.user is None:
            t1970 = time.gmtime(0)
            expires = time.strftime(
                'Expires=%a, %d-%b-%y %H:%M:%S GMT', t1970)
            self.send_header('Set-Cookie', 'user=;%s' % expires)
        else:
            self.send_header('Set-Cookie', 'user=%s' % self.user)
