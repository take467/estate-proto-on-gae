#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users

from gaeo.controller import BaseController
import urllib
import re
import cgi

from openid.server import server as OpenIDServer
from openid.extensions import sreg
from openid.store.filestore import FileOpenIDStore
from openid.consumer import discover

import logging
import time

class OidController(BaseController):
    lastCheckIDRequest = {}
    approved = {}

    def before_action(self):

      self.server = OpenIDServer.Server.server_instance

      self.__setUser()
      self.server_name = self.request.environ['SERVER_NAME']
      self.server_port = int(self.request.environ['SERVER_PORT'])
      if self.server_port != 80:
        self.base_url = ('http://%s:%s/oid/' % (self.server_name, self.server_port))
      else:
        self.base_url = 'http://%s/oid/' % (self.server_name,)
      if self.user:
        self.loginname =  self.user.email()
        self.auth_url = users.create_logout_url("/oid/login")
        self.auth_url_text = 'ログアウト'
        self.openid_url = self.base_url + 'id/' + str(self.user.user_id())
      else:
        self.loginname = '未ログイン'
        self.auth_url = users.create_login_url("/oid/login")
        self.auth_url_text = 'ログイン'

      self.endpoint_url  = self.base_url + "openidserver"
      self.trust_root    = self.base_url
      self.openid_server = self.base_url + "openidserver"
      self.server.setEndpoint(self.endpoint_url)

    def index(self):
      self.x_xrds_location = self.base_url + 'serveryadis'

    def allow(self):
        # pretend this next bit is keying off the user's session or something,
        # right?
        if self.user:
          request = OidController.lastCheckIDRequest.get(self.user.user_id())

        query = self.params
        if 'yes' in query:
            if 'login_as' in query:
                #self.user = query['login_as']
                #self.user = self.__getUserByID(query['login_as'])

                pass

            if request.idSelect():
                identity = self.base_url + 'id/' + query['identifier']
            else:
                identity = request.identity

            trust_root = request.trust_root
            if query.get('remember', 'no') == 'yes':
                wk = (identity, trust_root)
                logging.debug("allow() approved[" + str(wk) + "] = 'always'")
                OidController.approved[wk] = 'always'

            response = self.__approved(request, identity)

        elif 'no' in query:
            response = request.answer(False)
        else:
            assert False, 'strange allow post.  %r' % (query,)

        self.__displayResponse(response)

    # ===== こいつがメイン！ =====
    def openidserver(self):
      if self.request.method.upper() == "GET":
        qs = self.request.environ['QUERY_STRING']
        if qs is None or qs == '':
          self.render(template="about")
          return
        if self.user is None:
          auth_url = users.create_login_url("/oid/openidserver?" + qs)
          self.redirect(auth_url)
          return

      request = None
      try:
        request = self.server.decodeRequest(self.params)
      except OpenIDServer.ProtocolError, why:
        self.__displayResponse(why)
        return

      logging.debug('openid.mode is ' + request.mode)
      if request.mode in ["checkid_immediate", "checkid_setup"]:
        self.__handleCheckIDRequest(request)
      else:
        response = self.server.handleRequest(request)
        self.__displayResponse(response)

    def login(self):
      #GET
      if self.request.method.upper() == "GET":
        if self.user:
          # ログイン済みならリダイレクト
          self.redirect("/oid/id/" +  str(self.user.user_id()))
        else:
          #self.success_to = "/"
          #self.fail_to = "/"
          self.redirect(users.create_login_url("/oid/login"))

      #POST
      if self.request.method.upper() == "POST":
        pass

    def id(self):
      self.x_xrds_location = self.base_url + 'yadis/'+self.params.get('id')
      self.claimed_id = self.base_url + "id/"+ self.params.get('id')
      pass

    def yadis(self):
      endpoint_url = self.base_url + 'openidserver'
      user_url = self.base_url + 'id/' + self.params.get('id')
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
            self.__send_header('Set-Cookie', 'user=;%s' % expires)
        else:
            self.__send_header('Set-Cookie', 'user=%s' % self.user)

    def __displayResponse(self, response):
        try:
            webresponse = self.server.encodeResponse(response)
        except OpenIDServer.EncodingError, why:
            text = why.response.encodeToKVForm()
            self.message = cgi.escape(text)
            self.render(template='error')
            return

        self.__send_response(webresponse.code)
        for header, value in webresponse.headers.iteritems():
            self.__send_header(header, value)
        self.__writeUserHeader()
        #self.end_headers()

        if webresponse.body:
            self.render(binary=webresponse.body)
        else:
            self.render(text=' webresponse.body is None @ __displayResponse(response)')


    def __send_response(self,code):
      self.response.set_status(code)

    def __send_header(self,header,value):
      self.response.headers[header] = str(value)

    def __setUser(self):
      #cookies = self.headers.get('Cookie')
      #if cookies:
      #  morsel = Cookie.BaseCookie(cookies).get('user')
      #  if morsel:
      #    self.user = morsel.value
      self.user = users.get_current_user()

    def __handleCheckIDRequest(self, request):
        is_authorized = self.__isAuthorized(request.identity, request.trust_root)
        if is_authorized:
            #response = OidController.approved(request)
            response = self.__approved(request)
            self.__displayResponse(response)
        elif request.immediate:
            response = request.answer(False)
            self.__displayResponse(response)
        else:
            if self.user:
              OidController.lastCheckIDRequest[self.user.user_id()] = request
            self.__showDecidePage(request)

    def __isAuthorized(self, identity_url, trust_root):
        if self.user is None:
            return False

        # http://{server}/oid/id/{user.email()}
        wk = self.base_url + 'id/' + str(self.user.user_id())
        logging.debug("__isAuthorized() [identity_url=" + identity_url + "][openid_url=" + wk + "]")
        if identity_url != wk:
            return False

        key = (identity_url, trust_root)
        logging.debug("__isAuthorized() approved.get(" + str(key) + ") is " + str( OidController.approved.get(key) ))
        return OidController.approved.get(key) is not None

    def __approved(self, request, identifier=None):
        response = request.answer(True, identity=identifier)
        self.__addSRegResponse(request, response)
        return response

    def __addSRegResponse(self, request, response):
        sreg_req = sreg.SRegRequest.fromOpenIDRequest(request)

        # In a real application, this data would be user-specific,
        # and the user should be asked for permission to release
        # it.
        sreg_data = {
            'nickname':self.user.email()
        }

        sreg_resp = sreg.SRegResponse.extractResponse(sreg_req, sreg_data)
        response.addExtension(sreg_resp)

    def __showDecidePage(self, request):
        id_url_base = self.base_url+'id/'
        # XXX: This may break if there are any synonyms for id_url_base,
        # such as referring to it by IP address or a CNAME.
        assert (request.identity.startswith(id_url_base) or 
                request.idSelect()), repr((request.identity, id_url_base))
        expected_user = request.identity[len(id_url_base):]

        template = ''
        if request.idSelect(): # We are being asked to select an ID
          template='decidepage1'
          self.id_url_base=id_url_base
          self.trust_root = request.trust_root

        elif expected_user == str(self.user.user_id()):
          # ログインしている同じユーザでの認証がリクエストされている
          template='decidepage2'
          self.identity=request.identity
          self.trust_root=request.trust_root
        else:
          template='decidepage3'
          self.expected_user= expected_user
          self.identity= request.identity
          self.trust_root=request.trust_root

        self.render(template=template)



