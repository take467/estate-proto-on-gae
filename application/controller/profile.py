#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController
from google.appengine.ext import db

from google.appengine.api import users
from model.profile import Profile
from model.package import Package
from model.attribute import Attribute
import json
from google.appengine.api import images
from getimageinfo import getImageInfo
import yaml

# /product/show/:id 
class ProfileController(BaseController):
    def before_action(self):
      user = users.get_current_user()
      if user:
        self.url = users.create_logout_url("/")
        self.url_text = 'ログアウト'
      else:
        self.url = users.create_login_url(self.request.url)
        self.url_text = 'ログイン'

    def json(self):
      id = self.params.get('id')
      data = {}
      if id:
        p = Profile().get_by_id(int(id))
        if p:
          data = {'id':id,'organization':p.organization,'section':p.section,'last_name':p.last_name,'first_name':p.first_name,'title':p.title,'tel_no':p.tel_no,'email':p.email}
      self.render(json=self.to_json(data))
        
    def attribute(self):
      key = self.params.get('id')
      self.profile  = Profile.get(key)
      self.packages = Package.all()
      pass

    def attr_json(self):
      profile = Profile().get(self.params.get('id'))
      page = 1
      total = 0
      rows = []
      data = {'page':page, 'total': total, 'rows': rows }
      if profile:
        results = db.GqlQuery("SELECT * FROM Attribute WHERE profile = :1",profile)
        total = results.count()
        if total > 0:
          for p in results:
            wk = {}
            val = p.val
            if p.config:
              #config=json.read(p.config)
              config=yaml.load(p.config)
              if config:
                query = "SELECT * FROM " + config['model_name'] + " WHERE code = :1 "
                results = db.GqlQuery(query,p.val)
                if results.count() > 0:
                  rec = results.get()
                  val = rec.name
              
            person = "%s %s" % (profile.last_name,profile.first_name)
            wk = {'id':p.key().id(),"cell":[p.key().id(),profile.organization,profile.section,person,p.group,p.label,val]}
            rows.append(wk)

        #wk = {'id':1,'cell':['1','purchased_package','購入パッケージ','パッケージA']}

	data = {'page':page, 'total': total, 'rows': rows }
      self.render(json=self.to_json(data))
        
    def show(self):
      pass

    def update(self):
      id = self.params.get('id')
      if id:
        p = self.params
        rec = Profile().get_by_id(int(id))
        rec.organization=p.get('organization')
        rec.section=p.get('section')
        rec.last_name=p.get("last_name")
        rec.first_nam=p.get("first_nam")
        rec.title=p.get("title")
        rec.tel_no=p.get("tel_no")
        rec.email=p.get("email")
        rec.claimed_id=p.get("claimed_id")
        rec.put()

      msg = {'status':'success'}
      self.render(json=self.to_json(msg))

    def cancell_package(self):
      items = self.params.get('items')
      # split by ','
      msg = {'status':'success'}
      #try:
      for id in items.split(','):
          if id != None and id != '':
            data = Attribute().get_by_id(int(id))
            if data:
              data.delete()
      #except Exception,e:
      #  msg = {'status':'error','msg':'例外が発生しました'}
 
      self.render(json=self.to_json(msg))

    def buy_package(self):
      key = self.params.get('profile_key')
      profile  = Profile.get(key)
      p_code = self.params.get('selected_package')

      wk = u"購入パッケージ"
      attr = Attribute(profile = profile,label=wk,name='purchased_package',val=p_code,config=json.write({'model_name':'Package'}))
      attr.put()

      msg = {'status':'success'}
      self.render(json=self.to_json(msg))

      pass

    def create(self):
      p = self.params
      profile = Profile(organization=p.get('organization'),section=p.get('section'),title=p.get("title"),last_name=p.get("last_name"),first_name=p.get('first_name'),tel_no=p.get('tel_no'),email=p.get("email"),claimed_id=p.get('claimed_id'))
      profile.put()

      msg = {'status':'success'}
      self.render(json=self.to_json(msg))

    def delete(self):
      items = self.params.get('items')
      # split by ','
      msg = {'status':'success'}
      #try:
      for id in items.split(','):
          if id != None and id != '':
            data = Profile().get_by_id(int(id))
            if data:
              data.delete()
      #except Exception,e:
      #  msg = {'status':'error','msg':'例外が発生しました'}
 
      self.render(json=self.to_json(msg))

    def index(self):

      query = self.params.get("query")
      qtype = self.params.get("qtype")

      sortname = self.params.get("sortname")
      sortorder = self.params.get("sortorder")
      if sortorder.upper() == "DESC":
        sortname = "-" + sortname

      lines = int(self.params.get("rp"))
      page = int(self.params.get("page"))
      offset = (page - 1) * lines
     
      total = Profile.all().count()
      if (query != None and query != '' ) and ( qtype != None and qtype != ''):
        if qtype == 'id':
          p = Profile().get_by_id(int(query))
          results = []
          results.append(p)
        else:
          sql = "SELECT * FROM Profile WHERE " + qtype + "= :1 "
          if offset > 0:
            sql = sql + " OFFSET=" + str(offset) 
          sql = sal +  " limit = " + str(lines)
          results = db.GqlQuery(sql,query)
      else:
        if sortname == "id" :
          results = Profile.all().fetch(offset=offset,limit=lines)
        elif sortname == "-id":
          results = Profile.all().fetch(offset=offset,limit=lines)
          results.reverse()
        else:
          results = Profile.all().order(sortname).fetch(offset=offset,limit=lines)

      rows = []
      for rec in results:
        name = "%s %s" % (rec.last_name,rec.first_name)
        link = '<a href="/profile/attribute/' + str(rec.key()) + '">詳細</a>'
        wk = {'id':rec.key().id(),"cell":[rec.key().id(),rec.organization,rec.section,name,rec.title,rec.tel_no,rec.email,link]}
        rows.append(wk)

      data = {'page':page, 'total': total, 'rows': rows }
      self.render(json=self.to_json(data))
