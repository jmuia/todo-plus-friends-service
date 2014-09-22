#!/usr/bin/env python

import logging
from datetime import datetime
from json     import dumps as json_stringify, loads as json_parse
from os       import environ
from time     import mktime

from google.appengine.api                  import users
from google.appengine.api.datastore_errors import BadValueError
from google.appengine.api.validation       import ValidationError
from google.appengine.ext                  import ndb
import webapp2

import lib.mixpanel as mixpanel



DEBUG         = ('Development' in environ.get('SERVER_SOFTWARE', 'Production'))
ORIGINS       = '*' # verify the jws host instead of locking origin
OPTIONS_CACHE = 365 * 24 * 60 * 60 # 1 year
KIK_SESSION   = 'X-Kik-User-Session'
KIK_JWS       = 'X-Kik-JWS'



allowed_methods = webapp2.WSGIApplication.allowed_methods
webapp2.WSGIApplication.allowed_methods = allowed_methods.union(('PATCH',))



def admin_only(func):
	def wrapper(self, *args, **kwargs):
		if not is_admin(self, *args, **kwargs):
			logging.info('user must be admin')
			self.redirect( users.create_login_url('/') )
		else:
			return func(self, *args, **kwargs)
	return wrapper

def is_admin(*args, **kwargs):
	if len(args) > 0 and isinstance(args[0],webapp2.RequestHandler):
		if args[0].request.headers.get('X-AppEngine-Cron'):
			return True
		elif args[0].request.headers.get('X-AppEngine-QueueName'):
			return True
	return DEBUG or users.is_current_user_admin()

def future_iterator(futures):
	while futures:
		if len(futures) == 1:
			future = futures[0]
		else:
			future = ndb.Future.wait_any(futures)
		futures.remove(future)
		yield future



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
		if 'id' not in exclude and (include is None or 'id' in include) and self.key:
			props['id'] = self.key.id()
		for key, prop in self._properties.iteritems():
			if key not in exclude and (include is None or key in include):
				if hasattr(self, key):
					value = getattr(self, key)
					if isinstance(value, datetime):
						value = int( mktime(value.utctimetuple()) ) * 1000
					elif isinstance(value, ndb.Key):
						if fetch_keys:
							value = value.get().to_dict()
						else:
							value = value.id()
					elif isinstance(value, (list, tuple)) and len(value) > 0:
						if isinstance(value[0], datetime):
							value = [int( mktime(v.utctimetuple()) ) * 1000 for v in value]
						elif isinstance(value[0], ndb.Key):
							if fetch_keys:
								value = [e.to_dict() for e in ndb.get_multi(value)]
							else:
								value = [k.id() for k in value]
					props[key] = value
		return props



class BaseHandler(webapp2.RequestHandler):
	Model       = None
	_read_only  = []
	username    = None
	hostname    = None
	auth_params = None
	kik_session = None

	def initialize(self, *args, **kwargs):
		value = super(BaseHandler, self).initialize(*args, **kwargs)
		try:
			self.body_params = json_parse(self.request.body)
		except:
			self.body_params = {}
		self.params = {}
		self.params.update(self.request.params)
		self.params.update(self.body_params)
		try:
			session = self.request.headers.get(KIK_SESSION)
			if self.request.method in ('POST', 'PUT', 'PATCH'):
				jws = self.request.body
				payload = None
			else:
				jws = self.request.headers[KIK_JWS]
				payload = self.request.path
			from lib.jws import get_verified_data
			self.username, self.hostname, self.auth_params, self.kik_session = get_verified_data(jws, expected=payload, session_token=session)
		except:
			pass
		return value

	def _populate_entity(self, entity):
		props = self.Model._include
		if props is None:
			props = self.Model._properties.keys()
		for prop in self.Model._exclude:
			if prop in props:
				props.remove(prop)
		for prop in self._read_only:
			if prop in props:
				props.remove(prop)
		if 'id' in props:
			props.remove('id')
		if self.auth_params is not None:
			params = self.auth_params
		else:
			params = self.body_params
		for prop in props:
			if prop in params:
				value = params[prop]
				prop_field = getattr(self.Model, prop)
				if isinstance(prop_field, ndb.ComputedProperty):
					continue
				elif isinstance(prop_field, ndb.DateTimeProperty):
					if prop_field._repeated:
						try:
							value = [datetime.utcfromtimestamp( int(v/1000.0) ) for v in value]
						except:
							raise BadValueError('failed to parse datetime')
					else:
						try:
							value = datetime.utcfromtimestamp( int(value/1000.0) )
						except:
							raise BadValueError('failed to parse datetime')
				elif isinstance(prop_field, ndb.KeyProperty):
					if prop_field._repeated:
						value = [ndb.Key(prop_field._kind, v) for v in value]
						if None in ndb.get_multi(value):
							raise BadValueError('stored key must reference an existing entity')
					else:
						value = ndb.Key(prop_field._kind, value)
						if value.get() is None:
							raise BadValueError('stored key must reference an existing entity')
				entity.populate(**{ prop: value })

	def handle_exception(self, exception, debug):
		logging.exception(exception)
		if isinstance(exception, BadValueError) or isinstance(exception, ValidationError):
			self.response.set_status(400)
		else:
			self.response.set_status(500)
		self.response.write('An error occurred.')
		mixpanel.smart_flush()

	def security_headers(self):
		self.response.headers['X-Frame-Options'] = 'DENY'

	def cache_header(self, cache_life=0):
		if cache_life:
			self.response.headers['Cache-Control'] = 'public, max-age=%s' % cache_life
		else:
			self.response.headers['Cache-Control'] = 'no-cache'

	def cors_headers(self):
		self.response.headers['Access-Control-Allow-Origin' ] = ORIGINS
		self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, %s, %s' % (KIK_SESSION, KIK_JWS)
		self.response.headers['Access-Control-Max-Age'      ] = str(OPTIONS_CACHE)

	def options(self, *args, **kwargs):
		self.security_headers()
		self.cors_headers()
		self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
		self.cache_header(OPTIONS_CACHE)

	def respond(self, data, content_type='application/json', cache_life=0, headers={}):
		self.security_headers()
		self.cors_headers()
		self.cache_header(cache_life)

		for header, value in headers.items():
			if header == 'Content-Type':
				content_type = value
			else:
				self.response.headers[header] = value

		if content_type == 'application/json':
			if isinstance(data, BaseModel):
				data = data.to_dict()
			elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], BaseModel):
				data = [e.to_dict() for e in data]
			data = json_stringify(data, separators=(',',':'))

		# Let me begin with an apology. The Access-Control-Expose-Headers header is
		# not supported on most devices and prevents me from sending the session
		# token in a header. Instead of poluting the body of the response I have
		# decided to polute the Content-Type header with an extra parameter that
		# the client can read (because it is a "simple" header). I apologise for the
		# hackery that is below.
		if self.kik_session:
			content_type += '; kik-session=%s' % self.kik_session

		self.response.headers['Content-Type'] = content_type
		self.response.out.write(data)
		mixpanel.smart_flush()

	def respond_error(self, code, message='', cache_life=0, headers={}):
		self.response.set_status(code)
		self.security_headers()
		self.cors_headers()
		self.cache_header(cache_life)
		for header, value in headers.items():
			self.response.headers[header] = value
		if 'Content-Type' not in headers:
			self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(message)
		mixpanel.smart_flush()



class RESTHandler(BaseHandler):
	def get_list(self):
		return [e for e in self.Model.query().fetch() if self._can_do('read', e)]
	def can_create(self, entity): return False
	def can_read(self, entity): return False
	def can_update(self, entity): return False
	def can_delete(self, entity): return False
	def _can_do(self, action, *args):
		func = getattr(self, 'can_'+action)
		if isinstance(func, bool):
			return func
		else:
			try:
				return func(*args) or False
			except:
				return False

	def get(self, entity_id):
		if entity_id and entity_id.isdigit():
			entity_id = int(entity_id)
		if not entity_id:
			if self.get_list:
				entities = self.get_list()
			else:
				entities = None
			if entities is None:
				self.respond_error(403, 'forbidden')
			else:
				self.respond(entities)
		else:
			entity = self.Model.get_by_id(entity_id)
			if entity is None:
				self.respond_error(404, 'not found')
			else:
				if not self._can_do('read', entity):
					self.respond_error(403, 'forbidden')
				else:
					self.respond(entity)

	def post(self, entity_id):
		if entity_id and entity_id.isdigit():
			entity_id = int(entity_id)
		if entity_id:
			existing_entity = self.Model.get_by_id(entity_id)
			if existing_entity is None:
				self.respond_error(404, 'not found')
				return
		else:
			existing_entity = None
		if entity_id:
			entity = self.Model(id=entity_id)
		else:
			entity = self.Model()
		self._populate_entity(entity)
		if entity_id:
			if not self._can_do('update', entity, existing_entity):
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)
		else:
			if not self._can_do('create', entity):
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)

	def put(self, entity_id):
		if entity_id and entity_id.isdigit():
			entity_id = int(entity_id)
		if not entity_id:
			self.respond_error(405, 'method not allowed')
			return
		existing_entity = self.Model.get_by_id(entity_id)
		entity = self.Model(id=entity_id)
		self._populate_entity(entity)
		if existing_entity:
			if not self._can_do('update', entity, existing_entity):
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)
		else:
			if not self._can_do('create', entity):
				self.respond_error(403, 'forbidden')
			else:
				entity.put()
				self.respond(entity)

	def patch(self, entity_id):
		if entity_id and entity_id.isdigit():
			entity_id = int(entity_id)
		if not entity_id:
			self.respond_error(405, 'method not allowed')
			return
		existing_entity = self.Model.get_by_id(entity_id)
		if existing_entity is None:
			self.respond_error(404, 'not found')
			return
		entity = self.Model(key=existing_entity.key)
		for prop, _ in self.Model._properties.iteritems():
			prop_field = getattr(self.Model, prop)
			if not isinstance(prop_field, ndb.ComputedProperty):
				entity.populate(**{ prop: getattr(existing_entity, prop) })
		self._populate_entity(entity)
		if not self._can_do('update', entity, existing_entity):
			self.respond_error(403, 'forbidden')
		else:
			entity.put()
			self.respond(entity)

	def delete(self, entity_id):
		if entity_id and entity_id.isdigit():
			entity_id = int(entity_id)
		if not entity_id:
			self.respond_error(405, 'method not allowed')
			return
		entity = self.Model.get_by_id(entity_id)
		if entity is None:
			self.respond_error(404, '')
		else:
			if not self._can_do('delete', entity):
				self.respond_error(403, '')
			else:
				entity.key.delete()
				self.respond(entity)
