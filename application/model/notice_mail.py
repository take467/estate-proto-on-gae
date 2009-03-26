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

  def send_confirm(self,request,inquiry):
    server_url = request.environ['SERVER_NAME'] +":" + request.environ['SERVER_PORT']
    link  = "http://" + server_url + "/inquiry/show/" + str(inquiry.key().id())

    s = u"お問い合わせをお受け致しました"
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
""" % (inquiry.from_email,inquiry.key().id(),server_url)
    body = s.encode('utf-8')
    if mail.is_email_valid(inquiry.from_email):
      mail.send_mail(sender="supuremo <fuji1967@gmail.com>", to=inquiry.from_email, subject=subject, body=body)

  def notice(self,request,inquiry):

    server_url = request.environ['SERVER_NAME'] +":" + request.environ['SERVER_PORT']
    link  = "http://" + server_url + "/inquiry/show_by_id/" + str(inquiry.key().id())
   
    wk = ""
    if inquiry.category:
      wk = inquiry.category.name

    s=u"[お問い合わせ番号:%06d] %s" % (inquiry.key().id(),wk)
    subject=s.encode('utf-8')

    s=u"""
%sさん

お問い合わせが届いています。
%s
--
  http://%s/
""" % (inquiry.to,link,server_url)

    body = s.encode('utf-8')
    if mail.is_email_valid(inquiry.to):
      mail.send_mail(sender="supuremo <fuji1967@gmail.com>", to=inquiry.to, subject=subject, body=body)
