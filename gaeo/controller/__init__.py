# -*- coding: utf-8 -*-
#
# Copyright 2008 GAEO Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""GAEO controller package
"""

import new
import os
import re
import logging

from google.appengine.ext.webapp import template

import gaeo
import errors
import helper

class BaseController(object):
    """The BaseController is the base class of action controllers.
        Action controller handles the requests from clients.
    """
    def __init__(self, hnd, params = {}):
        self.hnd = hnd
        self.resp = self.response = hnd.response
        self.req = self.request = hnd.request
        self._env = self.request.environ # shortcut
        self.params = params

        rp = hnd.request.params.mixed()
        for k in rp:
            self.params[k] = hnd.request.get(k)

        self._controller = params['controller']
        self._action = params['action']
        self.has_rendered = False
        self.__config = gaeo.Config()

        self.__tpldir = os.path.join(
            self.__config.template_dir,
            self._controller
        )
        self._template_values = {}

        # implement parameter nesting as in rails
        self.params=self.__nested_params(self.params)
        
        # detect the mobile platform
        #http://www.infinitezest.com/UserAgents/UserAgentFinder.aspx
        self._is_mobile = self.__detect_mobile()
        self._is_iphone = self.__detect_iphone()
        self._is_android = self.__detect_android()

        # alias the cookies
        self.cookies = self.request.cookies

        # create the session
        try:
            store = self.__config.session_store
            exec('from gaeo.session.%s import %sSession' %
                (store, store.capitalize()))
        
            self.session = eval('%sSession' % store.capitalize())(
                                hnd, '%s_session' % self.__config.app_name)
        except:
            raise errors.ControllerInitError('Initialize Session Error!')

        # add request method (get, post, head, put, ....)
        self._request_method = self.request.environ['REQUEST_METHOD'].lower()
        
        # tell if an ajax call (X-Request)
        self._is_xhr = self._env.has_key('HTTP_X_REQUESTED_WITH') and \
                        self._env['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest'
        

        # add helpers
        helpers = dir(helper)
        for h in helpers:
            if not re.match('^__', h):
                self.__dict__[h] = new.instancemethod(eval('helper.%s' % h), self, BaseController)

    def implicit_action(self):
        """
        Deprecated. developer should do initialization in the applications'
        application controller (application_init method).
        """
        pass 

    def before_action(self):
        pass
    
    def after_action(self):
        pass
        
    def getResponse(self):
      return self.resp

    def error(self,errno,msg="error"):
        self.hnd.error(errno)
        self.render(text=msg)

    def invalid_action(self):
        """ If the router went to an invalid action """
        self.hnd.error(404)
        self.render(text="Invalid action")

    def to_json(self, obj, **kwds):
        """ Convert a dict to JSON. Inspired from SimpleJSON """
        from gaeo.controller.jsonencoder import JSONEncoder
        
        if not kwds:
            return JSONEncoder(skipkeys=False, ensure_ascii=True, check_circular=True,
                allow_nan=True, indent=None, separators=None, encoding='utf-8',
                default=None).encode(obj)
        else:
            return JSONEncoder(
                skipkeys=False, ensure_ascii=True, check_circular=True,
                allow_nan=True, indent=None, separators=None,
                encoding='utf-8', default=None, **kwds).encode(obj)

    def render(self, *html, **opt):
        o = self.resp.out
        h = self.resp.headers

        # check the default Content-Type is 'text/html; charset=utf-8'
        h['Content-Type'] = 'text/html; charset=utf-8'
        #h['Last-Modified']= "Thu, 01 Jun 2030 00:00:00 GMT"
        h['Pragma']       = 'no-cache'
        h['Cache_Control']= 'no-store'
        h['Expires']      = 'now'
        if html:
            for h in html:
                o.write(h.decode('utf-8'))
        elif opt:
            # if the expires header is set
            if opt.has_key('expires'):
                h['Expires'] = opt.get('expires')
                
            if opt.has_key('html'):
                o.write(opt.get('html').decode('utf-8'))                
            elif opt.has_key('binary'):
                if opt.has_key('content_type'):
                  h['Content-Type'] = opt.get('content_type')
                else:
                  h['Content-Type'] = 'application/octet-stream'
                o.write(opt.get('binary'))

            elif opt.has_key('text'):
                h['Content-Type'] = 'text/plain; charset=utf-8'
                o.write(str(opt.get('text')).decode('utf-8'))
            elif opt.has_key('json'):
                #h['Content-Type'] = 'application/json; charset=utf-8'

                # DO NOT WORK EXCEPT 'text/html' on firefox
                h['Content-Type'] = 'text/html; charset=utf-8'
                s = opt.get('json').decode('utf-8')
                h['Content-Length'] = str(len(s))

                o.write(s)
            elif opt.has_key('xml'):
                h['Content-Type'] = 'text/xml; charset=utf-8'
                o.write(opt.get('xml').decode('utf-8'))
            elif opt.has_key('script'):
                h['Content-Type'] = 'text/javascript; charset=utf-8'
                o.write(opt.get('script').decode('utf-8'))
            elif opt.has_key('template'):
                context = self.__dict__
                if isinstance(opt.get('values'), dict):
                    context.update(opt.get('values'))
                o.write(template.render(
                    os.path.join(self.__tpldir,
                                 opt.get('template') + '.html'),
                    context
                ))
            elif opt.has_key('template_string'):
                context = self.__dict__
                if isinstance(opt.get('values'), dict):
                    context.update(opt.get('values'))
                from django.template import Context, Template
                t = Template(opt.get('template_string').encode('utf-8'))
                c = Context(context)
                o.write(t.render(c))
            elif opt.has_key('image'): # for sending an image content
                import imghdr
                img_type = imghdr.what('ignored_filename', opt.get('image'))
                h['Content-Type'] = 'image/' + img_type
                o.write(opt.get('image'))
            elif opt.has_key('css'): # for css rendering
                h['Content-Type'] = 'text/css'
                o.write(opt.get('css'))
            else:
                raise errors.ControllerRenderTypeError('Render type error')
        self.has_rendered = True

    def render_txt(self,  **opt):
      s = ''
      context = self.__dict__
      if opt.has_key('template'):
        if isinstance(opt.get('values'), dict):
          context.update(opt.get('values'))
        s = template.render( os.path.join(self.__tpldir,opt.get('template') + '.txt'), context)
      elif opt.has_key('template_string'):
        if isinstance(opt.get('values'), dict):
          context.update(opt.get('values'))
        from django.template import Context, Template
        t = Template(opt.get('template_string').encode('utf-8'))
        c = Context(context)
        s = t.render(c)

      return s


    def skip_rendering(self):
      self.has_rendered = True
 
    def redirect(self, url, perm = False):
        self.has_rendered = True # dirty hack, make gaeo don't find the template
        self.hnd.redirect(url, perm)

    def respond_to(self, **blk):
        """ according to self.params['format'] to respond appropriate stuff
        """
        if self.params.has_key('format') and blk.has_key(self.params['format']):
            logging.error(self.params['format'])
            blk[self.params['format']]()

    def __detect_mobile(self):
        h = self.request.headers

        # wap.wml
        ha = h.get('Accept')
        if ha and (ha.find('text/vnd.wap.wml') > -1 or ha.find('application/vnd.wap.xhtml+xml') > -1):
            return True
        
        wap_profile = h.get('X-Wap-Profile')
        profile = h.get("Profile")
        opera_mini = h.get('X-OperaMini-Features')
        ua_pixels = h.get('UA-pixels')
        
        if wap_profile or profile or opera_mini or ua_pixels:
            return True
        
        # FIXME: add common user agents
        common_uas = ['sony', 'noki', 'java', 'midp', 'benq', 'wap-', 'wapi']
        
        ua = h.get('User-Agent')
        if ua and ua[0:4].lower() in common_uas:
            return True
        
        return False
        
    def __detect_iphone(self):
        """ for detecting iPhone/iPod """
        ua = self.request.headers.get('User-Agent')
        if ua:
            ua = ua.lower();
            return ua.find('iphone') > -1 or ua.find('ipod') > -1
        else:
            return False

    def __detect_android(self):
		""" for detecting android """
		ua = self.request.headers.get('User-Agent')
		if ua:
		    ua = ua.lower();
		    return ua.find('android') > -1
		else:
		    return False
            

    # Helper methods for parameter nesting as in rails
    def __appender(self,dict,arr,val):
            if len(arr) > 1:
                try:
                    dict[arr[0]]
                except KeyError:
                    dict[arr[0]]={}
                return {arr[0]: self.__appender(dict[arr[0]],arr[1:],val)}
            else:
                dict[arr[0]]=val
                return 

    def __nested_params(self,prm):
        prm2={}
        for param in prm:
            parray = param.replace(']',"").split('[')
            if len(parray) == 1:
                parray = parray[0].split('-')
            self.__appender(prm2,parray,prm[param])
        return prm2
        
