#!/usr/bin/env python

from json import dumps as to_json, loads as from_json
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2



# This is for monitoring purposes only
class HealthHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write('200')



# Base handler data
class BaseHandler(webapp2.RequestHandler):
	# Setup request parameters
	def initialize(self, *args, **kwargs):
		value = super(BaseHandler, self).initialize(*args, **kwargs)
		self.params = from_json(self.request.body)
		return value

	# Send response JSON object
	def respond(self, data):
		self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
		self.response.headers['Access-Control-Allow-Origin' ] = '*'
		self.response.headers['Cache-Control'] = 'no-cache'
		self.response.headers['Content-Type' ] = 'application/json'
		self.response.out.write( to_json(data, separators=(',',':')) )



# User data

def verify_user(anonymous_id, host, signed_data):
	#TODO
	return False

#TODO: add user model



#TODO: add api handlers



# Router

app = webapp2.WSGIApplication([
	#TODO: add api methods
	(r'/health', HealthHandler),
], debug=False)
