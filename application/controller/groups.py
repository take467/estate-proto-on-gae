#!-*- coding:utf-8 -*-
from google.appengine.ext import db
from gaeo.controller import BaseController

from model.user_db import UserDb
from model.view import UserView
from model.profile import ProfileCore
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

    def edit(self):
      id = self.params.get('id')
      self.user_db = UserDb.get_by_id(int(id))
      pass

    def update(self):
      if self.request.method.upper() != "POST":
        return 

      id = self.params.get('id')
      g = UserDb.get_by_id(int(id))
      if g:
        g.name = self.params.get('name')
	g.put()

      data = {'status':'success'}
      self.render(json=self.to_json(data))

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
        # 紐づくProfileデータは、リンク関係を切るー＞ゴミ箱をつくってそこに入れる
        q = ProfileCore.all()
        q.filter("user_db_id = ",g)
        for p in q:
          p.user_db_id = None
          p.put()

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

      category = UserDb(user=self.user,service_type=self.params.get('service_type','p'))

      category.put()
      id = category.key().id()
      name = u'DB(' + str(id) + ')'
      if category.service_type == 'c':
        name = u'問い合せDB(' + str(id) + ')'
      category.name = name
      category.put()

      # ついでにビューもつくってしまう
      cols = None
      if category.service_type == 'c':
        # 問い合わせフォーム専用ビュー
        cols = self.__set_inquiry_config(ProfileCore.disp_columns)
      else:
        cols = copy.deepcopy(ProfileCore.disp_columns)

      v = UserView(user_db_id = category,config=yaml.dump(cols))
      v.put()
      id= v.key().id()
      v.name=u'ビュー('+str(id)+')'
      v.put()
      # カレントのビューをこれにするためにクッキーにセット
      data={'status':'success','r':'/','cv_id':str(v.key().id())}

      self.render(json=self.to_json(data))

    def __set_inquiry_config(self,org_columns):
      cols = []

      #問い合わせ番号(inquiryのid)
      # 名前を Inquiry[id] とかにしたほうがよかったか？
      cols.append({'name':'iq_id','label':u'問い合せ番号','checked':'checked','width':'80','align':'right','type':'text','hidden':'false','search_refinement':'false'})
      #問い合わせ日
      cols.append({'name':'iq_post_at','label':u'問い合せ日','checked':'checked','width':'100','align':'left','type':'date','format':'yyyy/mm/dd','search_refinement':'false','hidden':'false'})
      #ステータス
      cols.append({'name':'iq_status','label':u'ステータス','checked':'checked','width':'80','align':'left','type':'select','search_refinement':True,'hidden':'true'})
      #タイトル
      cols.append({'name':'title','label':u'件名','checked':'checked','width':'100','align':'left','type':'text','search_refinement':'false','hidden':'false'})
      #送信者(E-Mail)
      for col in org_columns:
        if col['name'] != 'email':
          col['checked'] = ''
        cols.append(copy.copy(col)) 

      return cols
 


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

