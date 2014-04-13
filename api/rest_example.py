#!/usr/bin/env python

from lib.utils import RESTHandler
from model.rest_example import RestExample



class RestExampleHandler(RESTHandler):
	Model = RestExample
	def can_create(self, entity): return True
	def can_read(self, entity): return True
	def can_update(self, entity): return True
	def can_delete(self, entity): return True



routes = [
	(r'/rest-example/(\d*)', RestExampleHandler),
]
