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

from google.appengine.api import mail

class NoticeMail:
  def notice_share(self,request,share_user):

    view = share_user.share_view_id
    udb = view.user_db_id
    owner_email = udb.user.email()
    s = u"%sさんがDBを公開しました。" % owner_email
    subject=s.encode('utf-8')

    s=u"""
%sさんがデータベース[%s]のビュー[%s]をあなたに公開しました。　

-- 
  noticed by estate-proto <http://estate-proto.appsopt.com/>
""" % (owner_email,udb.name,view.name)
    body = s.encode('utf-8')
    if mail.is_email_valid(owner_email):
      mail.send_mail(sender="estate-proto <takeshi.fujisawa@gmail.com>", to=share_user.email, subject=subject, body=body)
      return True
    else:
      return False
