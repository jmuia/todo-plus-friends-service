#!/usr/bin/env python

from sys import path
from os  import listdir
path.append('./')

import webapp2

from lib.utils import DEBUG



routes = []
for file_name in listdir('api'):
	if not file_name.startswith('.') and file_name.endswith('.py') and file_name != '__init__.py':
		api_name   = file_name[:-3]
		api_module = __import__('api.%s' % api_name).__getattribute__(api_name)
		routes    += api_module.routes



app = webapp2.WSGIApplication(routes, debug=DEBUG)
