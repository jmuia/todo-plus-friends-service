#!/usr/bin/env python

import sys
import os
sys.path.append('./')

import webapp2
from google.appengine.ext import ndb

from lib.utils import DEBUG

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))

routes = []
for file_name in os.listdir('api'):
	if not file_name.startswith('.') and file_name.endswith('.py') and file_name != '__init__.py':
		api_name   = file_name[:-3]
		api_module = __import__('api.%s' % api_name).__getattribute__(api_name)
		routes    += api_module.routes

app = ndb.toplevel(webapp2.WSGIApplication(routes, debug=DEBUG))
