#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.controller import BaseController

from model.user_db import UserDb
from model.user_db_master import UserDbMaster
from model.view import UserView
from model.profile import ProfileCore
from model.inquiry import *
from model.share_user import ShareUser
from google.appengine.api import users
import yaml
import copy
import csv
import logging

class GroupsController(BaseController):
    def before_action(self):
      self.user = users.get_current_user()
      self.v_id = None
      if 'cv_id' in self.cookies:
        self.v_id = self.cookies['cv_id']
      pass

    def sample(self):

      self.skip_rendering()
      res = self.getResponse()
      res.headers['Content-Type'] = "application/x-csv;charset:Shift_JIS"
      res.headers["Content-Disposition"]="attachment; filename=" + "e-sample.csv"

      labels = []
      names   = []
      i = 0
      for col in ProfileCore.disp_columns:
        if col['type'] != 'hidden':
          labels.append( self.__conv(col['label'],'cp932'))
          names.append('"' + col['name'] + '"')


      wk = '#'+','.join(labels) + "\r\n"
      res.out.write(wk)
      wk = ','.join(names) + "\r\n"
      res.out.write(wk.encode('cp932'))

    def import_csv(self):
      if self.request.method.upper() == "GET":
        pass

      if self.request.method.upper() == "POST":
        data={'status':'success','msg':'アップロードが完了しました','r':'/'}
        if not self.user:
          self.render(json=self.to_json({'status':'error','msg':'不正なリクエスト'}))
          return

        # いったんワークエリアにデータをコピー
        bin = self.params.get('file')
        if not bin:
          self.render(json=self.to_json({'status':'error','msg':'ファイルを指定してください'}))
          return

        fname =  self.request.body_file.vars['file'].filename
        udb = UserDb(user=self.user,name=unicode(fname,self.__guess_charset(fname)))
        udb.put()

        # ついでにビューもつくってしまう (viewのカラムのcheckedを一反外す)
        v = UserView(user_db_id = udb)
        v.put()
        # カレントのビューをこれにするためにcv_idをセット
        data['cv_id']=str(v.key().id())

        # viewのカラムのcheckedを一反外し、csvにあるカラムのみ有効にする
        config = copy.deepcopy(ProfileCore.disp_columns)
        for col in config:
          if col['type'] != 'hidden':
            col['checked'] = ''

        #try:
        lines = []
        colinfo = None
        for line in bin.splitlines():
          if line[0] == '#' or line[0:2] == '"#':
            continue

          # カラム情報の取得
          if not colinfo:
            for row in csv.reader(line):
              for e in row:
                if colinfo == None:
                  colinfo = []
                colinfo.append(e)
                # カラムにcheckedをいれる
                for col in config:
                  if col['name'] == e:
                     col['checked'] = 'checked'
                     break

            #data['msg'] = '|'.join(colinfo) 
            v.config = yaml.dump(config)
            v.put()
          else:
            rec = ProfileCore(user_db_id=udb,user=self.user)
            rec.put()
            cols = copy.deepcopy(colinfo)
            wk = []
            for row in csv.reader(line):
              for e in row:
                name = cols.pop(0)
                if name:
                  setattr(rec,name,unicode(e,self.__guess_charset(e)))
                  #wk.append("(%s,%s)" % (name,e))

            #data['msg'] = '|'.join(wk) 
            rec.put()

        #except Exception, ex:
        #  data = {'status':'error','msg':'ファイルの読み込みに失敗しました'}
         
        self.render(json=self.to_json(data))

        pass

    def shared_member_list(self):
      #自分のDBをとりだす
      dbs = UserDb.all()
      dbs.filter('user =',self.user)

      members = {}
      for db in dbs:
        views = UserView.all()
        views.filter('user_db_id = ',db) 
        for v in views:
          # shareしているユーザの取得
          share_users = ShareUser.all()
          share_users.filter(' share_view_id = ',v)
          for su in share_users:
            if su.email in  members:
              members[su.email].append(su)
            else:
              members[su.email]=[su]

          self.member_list = []
          for m in members.keys():
            self.member_list.append({'email':m,'share_views':members[m]})
              

    def shared_treeview(self):
      self.user_dbs= []

      dbs = {}
      for u in db.GqlQuery("SELECT * FROM ShareUser WHERE email = :1",self.user.email()):
        id =  u.share_view_id.user_db_id.key().id() 
        if id in dbs:
          dbs[id].append(u)
        else:
          dbs[id] = [u]

      # keyでループ
      for id in dbs.keys(): 
        udb =  UserDb.get_by_id(id)
        self.user_dbs.append({'db':udb,'share_users':dbs[id]})

      #self.render(template='treeview')


    def treeview(self):
      self.user_dbs = []
      for u in db.GqlQuery("SELECT * FROM UserDb WHERE user = :1",self.user):
        list = db.GqlQuery("SELECT * FROM UserView WHERE user_db_id = :1",u)
        self.user_dbs.append({'db':u,'views':list})

    def edit_mail_template(self):
      id = self.params.get('id')
      self.user_db = UserDb.get_by_id(int(id))

      if self.request.method.upper() == "GET":

	values={'id':'{{id}}','db_name':'{{db_name}}','name':'{{name}}','reply_content':'{{reply_content}}'}
        self.id = '{{id}}'
        self.db_name = '{{db_name}}'
        self.name = '{{name}}'
        self.reply_content = '{{reply_content}}'

        self.confirm_mail_subject = self.user_db.getProperty('confirm_mail_subject')
        if not self.confirm_mail_subject:
          self.confirm_mail_subject = self.render_txt(template='confirm_mail_subject',values=values)

        self.confirm_mail_body = self.user_db.getProperty('confirm_mail_body')
        if not self.confirm_mail_body:
          self.confirm_mail_body = self.render_txt(template='confirm_mail_body',values=values)

        self.reply_mail_subject = self.user_db.getProperty('reply_mail_subject')
        if not self.reply_mail_subject:
          self.reply_mail_subject = self.render_txt(template='reply_mail_subject',values=values)

        self.reply_mail_body = self.user_db.getProperty('reply_mail_body')
        if not self.reply_mail_body:
          self.reply_mail_body = self.render_txt(template='reply_mail_body',values=values)

      if self.request.method.upper() == "POST":
        self.config = yaml.load(self.user_db.config)
        self.config['confirm_mail_subject'] = self.params.get('confirm_mail_subject')
        self.config['confirm_mail_body'] = self.params.get('confirm_mail_body')
        self.config['reply_mail_subject'] = self.params.get('reply_mail_subject')
        self.config['reply_mail_body'] = self.params.get('reply_mail_body')
        self.user_db.config = yaml.dump(self.config)
        self.user_db.put()
        self.render(template='update_mail_template')

    def edit(self):
      id = self.params.get('id')
      self.user_db = UserDb.get_by_id(int(id))

      if self.user_db.service_type == 'c':
        self.config = yaml.load(self.user_db.config)
        self.render(template="inquiry_edit")
      pass

    def update(self):
      if self.request.method.upper() != "POST":
        return 

      #logging.debug("[GroupsController#update] (params)="+ self.to_json(self.params) +")")

      id = self.params.get('edit_db_id')
      self.udb = UserDb.get_by_id(int(id))
      self.udb.name = self.params.get('edit_db_name')

      if self.udb.service_type != 'c':
        self.udb.put()
        data = {'status':'success'}
        self.render(json=self.to_json(data))
      else:

        # iq_open
        iq_open = self.params.get('iq_open','')
        # recipients 
        recipients = self.params.get('recipients',self.udb.user.email())

        # columns
        form_config = copy.deepcopy(self.udb.getProperty('form_config'))
        for col in form_config:
          if col['type'] == 'hidden':
            continue
          key = "disp_%s" % col['name']
          val = self.params.get(key,'None')

          if val == 'yes':
            col['checked']= 'checked'
          else:
            col['checked']= ''

        self.config = {'iq_open':iq_open,'recipients':recipients,'form_config':form_config}
        self.udb.config = yaml.dump(self.config)
        self.udb.put()
        self.render(template="inquiry_update")

    def delete(self):
      if self.request.method.upper() != "POST":
        return 

      id = self.params.get('id')
      g = UserDb.get_by_id(int(id))

      if g.user != self.user:
        data = {'status':'error','msg':'権限がありません'}
        self.render(json=self.to_json(data))
        return

      data = {'status':'success'}
      if g:

        # 紐づくデータは、リンク関係を切るー＞ゴミ箱をつくってそこに入れる
        # という仕様は面倒なのでまずは削除してしまう
        q = ProfileCore.all()
        q.filter("user_db_id = ",g)
        for p in q:
          p.delete()
          #p.user_db_id = None
          #p.put()

        q = Inquiry.all()
        q.filter("user_db_id = ",g)
        for p in q:
          p.delete()
          #p.user_db_id = None
          #p.put()

        # 紐づくViewを全て削除
        q = UserView.all()
        q.filter("user_db_id = ",g)
        for p in q:
          p.delete()

        g.delete()
        data = {'status':'success','r':'/'}

        if self.v_id and id == self.v_id:
  	  self.response.headers.add_header('Set-Cookie','cv_id=-1 ;expires=Fri, 5-Oct-1979 08:10:00 GMT')

      self.render(json=self.to_json(data))

    def create(self):
      data = {'status':'success'}
      if self.request.method.upper() != "POST":
        data = {'status':'error','msg':'forbidden method '}
        self.render(json=self.to_json(data))
        return

      udb = UserDb(user=self.user,service_type=self.params.get('service_type','p'))

      udb.put()
      id = udb.key().id()
      name = u'DB(' + str(id) + ')'
      if udb.service_type == 'c':
        name = u'問い合せDB(' + str(id) + ')'
        udb.config = yaml.dump({'recipients':udb.user.email(),'form_config':UserDbMaster.getFormConfig()})
      udb.name = name
      udb.put()

      # ついでにビューもつくってしまう
      v = UserView.newInstance(udb)
      # カレントのビューをこれにするためにクッキーにセット
      data={'status':'success','r':'/','cv_id':str(v.key().id())}

      self.render(json=self.to_json(data))

    def __set_inquiry_config(self,udb):
      cols = self.__set_inquiry_cols()
      cols.append({'name':'iq_content','label':u'お問い合わせ内容','cols':'60','rows':'10','type':'textarea','search_refinement':False,'hidden':'false','form':'must','checked':''})

      return config

    def __guess_charset(self,data):
      f = lambda d, enc: d.decode(enc) and enc

      try: return f(data, 'utf-8')
      except: pass
      try: return f(data, 'shift-jis')
      except: pass
      try: return f(data, 'euc-jp')
      except: pass
      try: return f(data, 'iso2022-jp')
      except: pass
      return None

    def __conv(self,data,enc):
      charset = self.__guess_charset(data)
      u = data
      if charset:
        u = data.decode(charset)
      return u.encode(enc)

