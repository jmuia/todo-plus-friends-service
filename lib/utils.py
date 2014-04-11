#!/usr/bin/env python

import logging
from datetime import datetime
from json     import dumps as to_json, loads as from_json
from os       import environ
from time     import mktime

from google.appengine.api.datastore_errors import BadValueError
from google.appengine.api.validation       import ValidationError
from google.appengine.ext                  import ndb
import webapp2



DEBUG   = ('Development' in environ.get('SERVER_SOFTWARE', 'Production'))
ORIGINS = '*' # change this if you want to lock access by domain
OPTIONS_CACHE = 365 * 24 * 60 * 60 # 1 year



allowed_methods = webapp2.WSGIApplication.allowed_methods
webapp2.WSGIApplication.allowed_methods = allowed_methods.union(('PATCH',))



class BaseModel(ndb.Model):
	_include    = None
	_exclude    = []
	_fetch_keys = True

	def to_dict(self, include=None, exclude=None, fetch_keys=None):
		if include is None:
			if self._include is not None:
				include = self._include
		if exclude is None:
			exclude = []
		if fetch_keys is None:
			fetch_keys = self._fetch_keys
		exclude.extend(self._exclude)
		props = {}
		if 'id' not in exclude and (include is None or 'id' in include):
			props['id'] = self.key.id()
		for key, prop in self._properties.iteritems():
			if key not in exclude and (include is None or key in include):
				value = getattr(self, key)
				if isinstance(value, datetime):
					props[key] = int( mktime(value.utctimetuple()) ) * 1000
				elif isinstance(value, ndb.Key):
					if fetch_keys:
						value = value.get().to_dict()
					else:
						value = value.id()
				elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], ndb.Key):
					if fetch_keys:
						value = [e.to_dict() for e in ndb.get_multi(value)]
					else:
						value = [k.id() for k in value]
				props[key] = value
		return props



class BaseHandler(webapp2.RequestHandler):
	def initialize(self, *args, **kwargs):
		value = super(BaseHandler, self).initialize(*args, **kwargs)
		try:
			self.body_params = from_json(self.request.body)
		except:
			self.body_params = {}
		self.params = {}
		self.params.update(self.request.params)
		self.params.update(self.body_params)
		return value

	def handle_exception(self, exception, debug):
		logging.exception(exception)
		if isinstance(exception, BadValueError) or isinstance(exception, ValidationError):
			self.response.set_status(400)
		else:
			self.response.set_status(500)
		self.response.write('An error occurred.')

	def options(self, *args, **kwargs):
		self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
		self.response.headers['Access-Control-Allow-Origin' ] = ORIGINS
		self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
		self.response.headers['Cache-Control'               ] = 'public, max-age=%s' % OPTIONS_CACHE

	def respond(self, data, content_type='application/json', cache_life=0):
		self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
		self.response.headers['Access-Control-Allow-Origin' ] = ORIGINS

		if cache_life:
			self.response.headers['Cache-Control'] = 'max-age=%s' % cache_life
		else:
			self.response.headers['Cache-Control'] = 'no-cache'

		if content_type == 'application/json':
			if isinstance(data, BaseModel):
				data = data.to_dict()
			elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], BaseModel):
				data = [e.to_dict() for e in data]
			self.response.headers['Content-Type'] = 'application/json'
			self.response.out.write( to_json(data, separators=(',',':')) )
		else:
			self.response.headers['Content-Type'] = content_type
			self.response.out.write(data)

	def respond_error(self, code, message='', cache_life=0):
		self.response.set_status(code)
		self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
		self.response.headers['Access-Control-Allow-Origin' ] = ORIGINS
		if cache_life:
			self.response.headers['Cache-Control'] = 'max-age=%s' % cache_life
		else:
			self.response.headers['Cache-Control'] = 'no-cache'
		self.response.headers['Content-Type' ] = 'text/plain'
		self.response.out.write(message)



class RESTHandler(BaseHandler):
	Model = None
	def can_list(self, entities):
		return False
	def can_create(self, entity):
		return False
	def can_read(self, entity):
		return False
	def can_update(self, entity):
		return False
	def can_delete(self, entity):
		return False

	def get(self, entity_id):
		if not entity_id:
			entities = self.Model.query().fetch()
			if self.can_list(entities) is False:
				self.respond_error(403, 'forbidden')
			else:
				self.respond(entities)
		else:
			entity = self.Model.get_by_id( int(entity_id) )
			if entity is None:
				self.respond_error(404, 'not found')
			else:
				if self.can_read(entity) is False:
					self.respond_error(403, 'forbidden')
				else:
					self.respond(entity)

	def post(self, entity_id):
		if entity_id:
			existing_entity = self.Model.get_by_id( int(entity_id) )
			if existing_entity is None:
				self.respond_error(404, 'not found')
		if entity_id:
			entity = self.Model(id=int(entity_id))
		else:
			entity = self.Model()
		entity.populate(**self.body_params)
		if entity_id:
			if self.can_update(entity) is False:
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)
		else:
			if self.can_create(entity) is False:
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)

	def put(self, entity_id):
		if not entity_id:
			self.respond_error(405, 'method not allowed')
			return
		existing_entity = self.Model.get_by_id( int(entity_id) )
		entity = self.Model(id=int(entity_id))
		entity.populate(**self.body_params)
		if existing_entity:
			if self.can_update(entity) is False:
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)
		else:
			if self.can_create(entity) is False:
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)

	def patch(self, entity_id):
		if not entity_id:
			self.respond_error(405, 'method not allowed')
			return
		entity = self.Model.get_by_id( int(entity_id) )
		if entity is None:
			self.respond_error(404, 'not found')
			return
		entity.populate(**self.body_params)
		if self.can_update(entity) is False:
			self.respond_error(403, 'forbidden')
		else:
			entity.put()
			self.respond(entity)

	def delete(self, entity_id):
		if not entity_id:
			self.respond_error(405, 'method not allowed')
			return
		entity = self.Model.get_by_id( int(entity_id) )
		if entity is None:
			self.respond_error(404, '')
		else:
			if self.can_delete(entity) is False:
				self.respond_error(403, '')
			else:
				entity.key.delete()
				self.respond(entity)
