#!-*- coding:utf-8 -*-

# import the webapp module
from google.appengine.ext import webapp
import datetime


# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def truncate(value,maxsize,stopper = '...'):
  """ truncates a string to a given maximum size and appends the stopper if needed """
  stoplen = len(stopper)
  if len(value) > maxsize and maxsize > stoplen:
    return value[:(maxsize-stoplen)] + stopper
  else:
    return value[:maxsize]

def timeJST (value):
  #     return value - datetime.timedelta(hours=18)
  return value + datetime.timedelta(hours=9)
  # SDK102 にしたら動作がかわった？??

register.filter(truncate)
register.filter(timeJST)
