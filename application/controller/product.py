#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController
from google.appengine.ext import db

from google.appengine.api import users
from model.product import Product
from model.profile import Profile
import json
from google.appengine.api import images
from getimageinfo import getImageInfo
import datetime

class JST(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=9)
    def dst(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return "JST"

# /product/show/:id 
class ProductController(BaseController):
    def before_action(self):
      self.logged_in = True
      self.claimed_id = None
      try:
        self.claimed_id = self.cookies['claimed_id']
        if self.claimed_id == None or self.claimed_id == '':
          self.logged_in = False
      except:
        self.logged_in = False

      self.profile = db.GqlQuery("SELECT * FROM Profile WHERE claimed_id = :1",self.claimed_id).get()



    def json(self):
      id = self.params.get('id')
      data = {}
      if id:
        p = Product().get_by_id(int(id))
        d = p.released_at + datetime.timedelta(hours=9)
        data = {'id':id,'package_code':p.package_code,'gernre_code':p.genre_code,'released_at':d.strftime('%Y/%m/%d'),'author':p.author,'title':p.title,'duration':p.duration,'filename':p.filename,'description':p.description}
      self.render(json=self.to_json(data))
        
    def thumbnail(self):
      if self.request.method.upper() == "GET":
        id =  self.params.get("id")
        if id:
          p = Product().get_by_id(int(id))
          if p:
            bin = p.thumbnail
            if bin:
              content_type,width,height,size = getImageInfo(bin)
              self.render(binary=bin,content_type = str(content_type))
            else:
              self.redirect('/img/now_printing.jpg')
          else:
            self.redirect('/img/now_printing.jpg')
        else:
          self.redirect('/img/now_printing.jpg')

      if self.request.method.upper() == "POST":
        id = self.request.get("thumbnail_product_id")
        file_data = self.request.get("up_file")
        res= {'status':'success','msg':"アップロードが完了しました"}

        if file_data == None:
          res= {'status':'error',"msg":"ファイルが不正です"}
        else:
          length = len(file_data)
          if length >= ( 1 * 1024 * 1024):
            wk = length / 1024 ;
            wk2 = "ファイルサイズが大きすぎます(%sKB)。1MB以下にしてください" % str(wk)
            res={ 'status': 'error','msg': wk2}
          else:
            # 値セット
            type = self.request.body_file.vars['up_file'].headers['Content-Type']
            name = self.request.body_file.vars['up_file'].filename.decode('utf-8')
            if id:
              p = Product().get_by_id(int(id))
              p.thumbnail = file_data
              p.thumbnail_filename= name
              p.put()
            else:
              res={ 'status': 'error','msg': '該当する商品が見つかりいません'}

        self.render(json=self.to_json(res))

    # 表示する前に、見る権利のある動画かどうかチェックするひつようあり
    # 運用でカバーして、契約外の動画をみていることがログのチェックでわかったら追加徴収するという手もあるが
    def show(self):
      if not self.logged_in:
        self.redirect("/login")
        return

      self.product = Product().get_by_id(int(self.params.get('id')))
      pass

    def update(self):
      id = self.params.get('id')
      if id:
        p = self.params
        r_year = p.get('release_year')
        r_month = p.get('release_month')
        r_day = p.get('release_day')

        release_date = datetime.datetime.now()
        try:
          release_date = datetime.datetime(int(r_year),int(r_month),int(r_day),0,0,0,0,JST())
        except:
          pass

        rec = Product().get_by_id(int(id))
        rec.package_code=p.get('package_code')
        rec.genre_code=p.get('genre_code')
        rec.title=p.get("title")
        rec.description=p.get("description")
        rec.released_at = release_date
        rec.author=p.get("author")
        rec.duration=p.get('duration')
        rec.filename=p.get('filename')
        rec.put()

      msg = {'status':'success'}
      self.render(json=self.to_json(msg))


    def create(self):
      p = self.params
      r_year = p.get('release_year')
      r_month = p.get('release_month')
      r_day = p.get('release_day')

      release_date = datetime.datetime.now()
      try:
        release_date = datetime.datetime(int(r_year),int(r_month),int(r_day),0,0,0,0,JST())
      except:
        pass
      product = Product(package_code=p.get('package_code'),genre_code=p.get('genre_code'),title=p.get("title"),author=p.get("author"),duration=p.get('duration'),filename=p.get('filename'),description=p.get("description"),released_at=release_date)
      product.put()

      msg = {'status':'success'}
      self.render(json=self.to_json(msg))

    def delete(self):
      items = self.params.get('items')
      # split by ','
      msg = {'status':'success'}
      #try:
      for id in items.split(','):
          # 本当は先にvolumesを削除
          if id != None and id != '':
            data = Product().get_by_id(int(id))
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
     
      total = Product.all().count()
      if (query != None and query != '' ) and ( qtype != None and qtype != ''):
        if qtype == 'id':
          p = Product().get_by_id(int(query))
          results = []
          results.append(p)
        else:
          #filter = qtype + "=" 
          #results = Product.all().filter(filter,query).fetch(offset=offset,limit=lines)
          #results = Product.all().filter("duration=",89).fetch(offset=offset,limit=lines)
          sql = "SELECT * FROM Product WHERE " + qtype + "= :1 "
          if offset > 0:
            sql = sql + " OFFSET=" + str(offset) 
          sql = sal +  " limit = " + str(lines)
          results = db.GqlQuery(sql,query)
      else:
        if sortname == "id" :
          results = Product.all().fetch(offset=offset,limit=lines)
        elif sortname == "-id":
          results = Product.all().fetch(offset=offset,limit=lines)
          results.reverse()
        else:
          results = Product.all().order(sortname).fetch(offset=offset,limit=lines)

      rows = []
      for rec in results:
        genre_name = ''
        if rec.genre():
          genre_name = rec.genre().name

        package_name = ''
        if rec.package():
          package_name = rec.package().name

        thumbnail_url = '<a href="javascript:void(0)" onclick="uploadThumbNail(' + str(rec.key().id()) + ')" >登録</a>'
        if rec.thumbnail:
          wk = '<a href="javascript:void(0)" onclick="disp_img(\'' + str(rec.key().id()) + '/' + rec.thumbnail_filename + '\')"><img src="/product/thumbnail/'+str(rec.key().id())+'/' + rec.thumbnail_filename + '" alt="dummy" width="24"></a> - '
          thumbnail_url  = wk.encode('utf-8') + thumbnail_url

        movie_url = '<a href="javascript:void(0)" onclick="play_movie(\'' + rec.filename + '\')" >play</a>'
        d = rec.released_at + datetime.timedelta(hours=9)
        wk = {'id':rec.key().id(),"cell":[rec.key().id(),package_name,genre_name,rec.title,d.strftime('%Y/%m/%d'),rec.author,rec.duration,thumbnail_url,rec.filename,movie_url]}
        rows.append(wk)

      data = {'page':page, 'total': total, 'rows': rows }
      self.render(json=self.to_json(data))
