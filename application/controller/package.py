#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController

from model.package import Package

class PackageController(BaseController):
    def create(self):
     try:
        packages = Package.all()
        for package in packages:
          name = self.params.get("name_%s" % package.code)
          id = self.params.get("package_%s" % package.code)
          wk = db.GqlQuery("SELECT * FROM Package WHERE code = :1",id).get()
          if wk != None:
            package.name=name
            package.code = id
            package.put()

        new = self.params['new_package']
        if new:
          id = self.params['new_package_code']
          package = Package(name=new, code=id)
          package.put()

        # URL '/package/' にリダイレクト
        self.redirect('/site/package/')
     except Exception, ex:
        # 例外メッセージを表示する
        self.render(text='Exception: %s' % ex)

    def delete(self):

      # パッケージに属する商品があったら削除できない
      res= {"status":"success","msg":"削除しました"}
      query = db.GqlQuery("SELECT * FROM Product WHERE genre_code = :1",self.params.get("code"))
      if query.count() > 0:
        res= {"status":"error","msg":"パッケージに属する商品があるため削除できません。"}
      else:
        genre = Package.get(db.Key(self.params.get("key")));
        if genre:
          genre.delete()
        else:
          res= {"status":"error","msg":"削除に失敗しました"}

      self.render(json=self.to_json(res))
