#!-*- coding:utf-8 -*-
from google.appengine.ext import db

from gaeo.controller import BaseController

from model.genre import Genre
from model.site import Site
from model.document import Document

class GenreController(BaseController):
    def create(self):
     try:
        genres = Genre.all()
        for genre in genres:
          name = self.params.get("name_%s" % genre.genre_code)
          id = self.params.get("genre_%s" % genre.genre_code)
          wk = db.GqlQuery("SELECT * FROM Genre WHERE genre_code = :1",id).get()
          if wk != None:
            genre.name=name
            genre.genre_code = id
            genre.put()

        new = self.params['new_genre']
        if new:
          id = self.params['new_genre_code']
          genre = Genre(name=new, genre_code=id)
          genre.put()

        # URL '/genre/' にリダイレクト
        self.redirect('/site/genre/')
     except Exception, ex:
        # 例外メッセージを表示する
        self.render(text='Exception: %s' % ex)

    def delete(self):

      # ジャンルに属する商品があったら削除できない
      res= {"status":"success","msg":"削除しました"}
      query = db.GqlQuery("SELECT * FROM Product WHERE genre_code = :1",self.params.get("code"))
      if query.count() > 0:
        res= {"status":"error","msg":"ジャンルに属する商品があるため削除できません。"}
      else:
        genre = Genre.get(db.Key(self.params.get("key")));
        if genre:
          genre.delete()
        else:
          res= {"status":"error","msg":"削除に失敗しました"}

      self.render(json=self.to_json(res))
