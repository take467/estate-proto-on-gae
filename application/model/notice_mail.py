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

  def send_reply(self,request,inquiry):
    server_url = request.environ['SERVER_NAME'] +":" + request.environ['SERVER_PORT']
    link  = "http://" + server_url + "/inquiry/show/" + str(inquiry.key().id())

    s = u"お問い合わせ番号[%06d]に対する回答" % inquiry.key().id()
    subject=s.encode('utf-8')

    id = inquiry.key().id()

    s=u"""
%s様

ご利用ありがとうございます。
 
%s

 今回いただいたごお問い合わせに関して、追加質問をいただく場合は、
 サイト内の「お問い合せ」のページから、
 お問い合わせ番号「%06d」を入力の上、送信ください。

 /=============================================================/
    http://%s/
 /=============================================================/
""" % (inquiry.from_email,inquiry.reply_content,id,server_url)
    body = s.encode('utf-8')
    if mail.is_email_valid(inquiry.from_email):
      mail.send_mail(sender="inquiry <fuji1967@gmail.com>", to=inquiry.from_email, subject=subject, body=body)

  ###########################################
  #  問い合わせをした人に通知
  ###########################################
  def send_confirm(self,request,inquiry):
    server_url = request.environ['SERVER_NAME'] +":" + request.environ['SERVER_PORT']
    link  = "http://" + server_url + "/inquiry/show/" + str(inquiry.key().id())

    s=u"[番号:%06d] %s" % (inquiry.key().id(),u"お問い合わせをお受け致しました")
    subject=s.encode('utf-8')

    s=u"""
%s様

 ご利用ありがとうございます。
 ご案内、回答まで今しばらくお待ちください。

 今回のご質問に関するお問合せ番号は「%06d」です。

 本メールアドレスは発信専用です。このメールへのご返信には、お応え
 致しかねますので、予めご了承ください。

 ■=============================================================■
    http://%s/
 ■=============================================================■
""" % (inquiry.profile().email,inquiry.key().id(),server_url)
    body = s.encode('utf-8')
    if mail.is_email_valid(inquiry.profile().email):
      mail.send_mail(sender="estate-prototype <fuji1967@gmail.com>", to=inquiry.profile().email, subject=subject, body=body)

  ###########################################
  #  担当者に通知
  ###########################################
  def notice(self,request,inquiry):

    server_url = request.environ['SERVER_NAME'] +":" + request.environ['SERVER_PORT']
    link  = "http://" + server_url + "/inquiry/show/" + str(inquiry.key().id())
   
    s=u"[お問い合わせ番号:%06d] %s" % (inquiry.key().id(),inquiry.title)
    subject=s.encode('utf-8')

    s=u"""
%sさん

お問い合わせが届いています。
%s
--
  http://%s/
""" % (inquiry.user_db().getProperty('recipients'),link,server_url)

    body = s.encode('utf-8')
    recipient = inquiry.user_db().getProperty('recipients')
    if mail.is_email_valid(recipient):
      mail.send_mail(sender="estate-prototype <fuji1967@gmail.com>", to=recipient, subject=subject, body=body)
