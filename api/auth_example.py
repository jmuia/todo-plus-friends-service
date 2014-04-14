#!/usr/bin/env python

from lib.utils import RESTHandler
from model.auth_example import AuthExample



class AuthExampleHandler(RESTHandler):
	Model = AuthExample
	def can_do(self, entity, *args):
		if entity.username != self.username:
			return False
		elif entity.hostname != self.hostname:
			return False
		else:
			return True
	can_create = can_do
	can_read   = can_do
	can_update = can_do
	can_delete = can_do



routes = [
	(r'/auth-example/(\d*)', AuthExampleHandler),
]
