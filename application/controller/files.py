#!-*- coding:utf-8 -*-
"""
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json

from google.appengine.ext import db
from gaeo.controller import BaseController
from model.file import File

class FilesController(BaseController):
    def delete(self):
      if self.request.method.upper() == "GET":
        return
      id = self.params['id']
      if not id:
        self.error(404)
        return

      res= {"status":"success","msg":"削除しました"}
      file = File.get_by_id(int(id))
      if file:
        file.delete()
      else:
        res= {"status":"error","msg":"削除に失敗しました"}

      self.render(json=self.to_json(res))
      

    def feed(self):
      id = self.params['id']
      if not id:
        self.error(404)
        return

      file = File.get_by_id(int(id))
      if not file:
        self.error(404)
        return

      self.render(binary=file.body,content_type=str(file.content_type))
      #self.render(binary=file.body,content_type='application/octet-strem')

    def index(self):
      self.files = File.all().order('-uploaded_at')

    def overwrite(self):
        pass

    def upload(self):
      if self.request.method.upper() == "GET":
        return

      file_data = self.request.get("up_file")
      res= {'status':'success','msg':"アップロードが完了しました"}

      if file == None:
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
          rec  = File(filename=name,orginal_filename=name,content_type=type,content_length=length,body=file_data) 
          rec.put()

      self.render(json=self.to_json(res))
