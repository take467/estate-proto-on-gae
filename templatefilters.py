#!-*- coding:utf-8 -*-

# import the webapp module
from google.appengine.ext import webapp
import datetime
import re


# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def truncate(value,maxsize=50,stopper = '...'):
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

def pre2markup(value):
  if value:
    description = re.sub("\n","<br/>",value)
    description = re.sub("\s","&nbsp;",description)
    return description
  else:
    return ''

def join(value,d):
  return d.join(value)

register.filter(truncate)
register.filter(timeJST)
register.filter(pre2markup)
register.filter(join)
