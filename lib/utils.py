#!/usr/bin/env python

from json import dumps as to_json, loads as from_json
from os import environ

import webapp2



DEBUG = ('Development' in environ.get('SERVER_SOFTWARE', 'Production'))



class BaseHandler(webapp2.RequestHandler):
	def initialize(self, *args, **kwargs):
		value = super(BaseHandler, self).initialize(*args, **kwargs)
		if ('Content-Type' in self.request.headers) and (self.request.headers['Content-Type'] == 'application/json'):
			self.params = from_json(self.request.body)
		else:
			self.params = {}
		return value

	def options(self, *args, **kwargs):
		self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
		self.response.headers['Access-Control-Allow-Origin' ] = '*'
		self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
		self.response.headers['Cache-Control'               ] = 'no-cache'

	def respond(self, data, content_type='application/json', cache_life=0):
		self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
		self.response.headers['Access-Control-Allow-Origin' ] = '*'

		if cache_life:
			self.response.headers['Cache-Control'] = 'max-age=%s' % cache_life
		else:
			self.response.headers['Cache-Control'] = 'no-cache'

		if content_type == 'application/json':
			self.response.headers['Content-Type'] = 'application/json'
			self.response.out.write( to_json(data, separators=(',',':')) )
		else:
			self.response.headers['Content-Type'] = content_type
			self.response.out.write(data)
