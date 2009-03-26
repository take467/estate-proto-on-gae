#!-*- coding:utf-8 -*-
from gaeo.controller import BaseController

from model.profile import Profile
from google.appengine.api import users
from google.appengine.ext import webapp,db

class SettingController(BaseController):
  def before_action(self):
    self.user = users.get_current_user()
    if self.user == None:
      self.response.out.write("Bad Request")
      return;
      pass

    results = db.GqlQuery("SELECT * FROM Profile WHERE user = :1",self.user)
    self.profile = results.get()

  def index(self):
    if self.profile == None:
      self.profile = Profile(user=self.user)

  def edit(self):
    if self.profile == None:
      self.response.out.write("Bad Request")
      return;

  def update(self):
    if self.request.method.upper() != "POST":
      return

    if self.profile == None:
      self.profile = Profile(user=self.user)
    self.profile.organization = self.params.get('organization')
    self.profile.section = self.params.get('section')
    self.profile.last_name = self.params.get('last_name')
    self.profile.first_name = self.params.get('first_name')
    self.profile.last_name_hira = self.params.get('last_name_hira')
    self.profile.first_name_hira = self.params.get('first_name_hira')
    self.profile.email = self.params.get('email')
    self.profile.tel_no = self.params.get('tel_no')
    self.profile.zip_code = self.params.get('zip_code')
    self.profile.prefecture = self.params.get('prefecture')
    self.profile.city = self.params.get('city')
    self.profile.address = self.params.get('address')

    self.profile.put()
