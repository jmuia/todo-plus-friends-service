#!/usr/bin/env python

from model.rest_example import RestExample
from lib.utils import BaseHandler


class RestExampleHandler(BaseHandler):
	Model = RestExample
	def can_create(self, entity): return True
	def can_read(self, entity): return True
	def can_update(self, entity, old_entity): return True
	def can_delete(self, entity): return True



routes = [
	(r'/rest-example/(\d*)', RestExampleHandler),
]
