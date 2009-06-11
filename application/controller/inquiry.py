#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController
from model.user_db import *
from model.inquiry import *
from model.notice_mail import *
from model.view import *

import re
import cgi
import copy
import logging
import datetime

class InquiryController(BaseController):
    #def before_action(self):
    #  self.server_name = self.request.environ['SERVER_NAME']
    #  self.server_port = int(self.request.environ['SERVER_PORT'])
    #  if self.server_port != 80:
    #    self.base_url = ('http://%s:%s/' % (self.server_name, self.server_port))
    #  else:
    #    self.base_url = 'http://%s/' % (self.server_name,)

    def edit(self):
      self.inquiry = Inquiry.get_by_id(int(self.params.get('id')))
      self.user_db = UserView.get_by_id(int(self.params.get('v')))
      self.config = yaml.load(self.user_db.config)

    def json(self):
      # ビューの確定
      id = self.cookies['cv_id']

      if id == None:
        self.render(json=self.to_json([]))
        return

      self.fields = []
      self.view = UserView.get_by_id(int(id))
      if self.view == None:
        self.render(json=self.to_json([]))
        return

      # inquiry 一覧を取得（flexigridの絞り込み条件に従って)
      self.config = yaml.load(self.view.config)

      query = self.params.get("query",'')
      qtype = self.params.get("qtype",'')

      sortname = self.params.get("sortname",'iq_id')
      if sortname.startswith("iq_"):
        sortname = sortname[3:]
      elif sortname.startswith("-iq_"):
        sortname = "-" + sortname[4:]
      sortorder = self.params.get("sortorder",'DESC')

      lines = int(self.params.get("rp",'15'))
      page = int(self.params.get("page",'1'))
      offset = (page - 1) * lines

      # 絞り込み項目が選択されていれば追加
      # Inquiry と Profileの両方の項目で絞り込みが発生するので、まずは
      # Inquiryをfetchしたあと自前でループしてPfrofile項目を絞り込む
      # RDBなら簡単なのに。。。
      add_filters =[]
      if self.view:
        configs =  yaml.load(self.view.config)
        for col in configs:
          if col['checked'] == 'checked':
            if col['type'] == 'radio' or col['type'] == 'select':

              flg = False
              if col['name'].startswith('iq_'): 
                # "iq_{name} => {name}
                name = col['name'][3:]
                if isinstance(getattr(Inquiry,name),db.StringProperty):
                  flg = True
                elif isinstance(getattr(ProfileCore,col['name']),db.StringProperty):
                  flg = True
              if flg:
                 val = self.params.get(col['name'])
                 if val != None and val != '':
                   add_filters.append({'name':col['name'],'val':val})

      results = []
      if (query != None and query != '' ) and ( qtype != None and qtype != ''):
        add_filters.append({'name':qtype,'val':query})

      p = None
      if (query != None and query != '' ) and  qtype == 'iq_id' and ( qtype != None and qtype != ''):
        try:
          p  = Inquiry.get_by_id(int(query))
        except:
          pass
        total = 0
        if p != None and (p.user == user):
          total = 1
          iqs=[p]
      else:
        logging.debug('>>> Inquiry.all() <<< [UDB]' + str( self.view.user_db_id.key().id()))
        p = Inquiry.all()
        p.filter(" user_db_id = ",self.view.user_db_id)
        for f in add_filters:
          if f['name'].startswith('iq_'): 
            # "iq_{name} => {name}
            name = f['name'][3:]
            p.filter(name + " = ",f['val'])
            logging.debug('>>> add filter <<< name = ' + f['val'])
        iqs = p.fetch(lines,offset)

      is_id_sort = False
      if sortname != 'id' and sortname != '-id' :
        if sortorder.upper() == 'DESC':
          sortname = '-' + sortname
        p.order(sortname)
      else:
        is_id_sort = True

      logging.debug(">>> p.count() is " + str(p.count()) + " <<<")

      # Profile の絞り込み項目で
      results = []
      for iq in iqs:
        is_added = True
        for f in add_filters:
          # Profile での絞り込みがあった！ 
          if not f['name'].startswith('iq_'): 
            pval = getattr(iq.profile(),col['name'])
            if pval != f['val']:
              is_added = False
        if is_added:
          results.append(iq) 

      if is_id_sort and (sortorder != None and sortorder.upper() == 'DESC'):
        results.reverse()


      rows = []
      total = len(results)
      for rec in results:
        wk = {'id':rec.key().id(),"cell":[rec.key().id()]}
        for col in self.config:
          if col['checked'] == 'checked':
            val = None
            clazz = None
            name = None
            if col['name'].startswith('iq_'): 
              # "iq_{name} => {name}
              name = col['name'][3:]
              val = getattr(rec,name)
              clazz = Inquiry
            else:
              name = col['name']
              val = getattr(rec.profile(),name)
              clazz = ProfileCore

            if col['type'] == 'radio' or col['type'] == 'select':
              udm = db.GqlQuery("SELECT  * FROM UserDbMaster WHERE name = :1",col['name']).get()
              for item in yaml.load(udm.yaml_data):
                if item['code'] == val:
                  val = item['name']

            if isinstance(getattr(clazz,name),db.DateTimeProperty):
              logging.debug(">>> BINGO <<< name is " + col['name'] + " val is " + str(val))
              wk2 = val + datetime.timedelta(hours=9)
              if 'format' in col:
                val = wk2.strftime(col['format'])
                #val = wk2.strftime('%Y/%m/%d')
              else:
                val = wk2.strftime('%Y/%m/%d %H:%M:%S')
            wk['cell'].append(val)

        rows.append(wk)

      data = {'page':page, 'total': total, 'rows': rows }
      self.render(json=self.to_json(data))
