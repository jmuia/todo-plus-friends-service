#!/usr/bin/env python

from model.example import Example
from lib.utils import BaseHandler



class CreateExampleHandler(BaseHandler):
	def post(self):
		example = Example(value=self.params['value'])
		example.put()
		self.respond({ 'example_id' : example.key.id() })

class ExampleHandler(BaseHandler):
	def get(self, example_id):
		example = Example.get_by_id( int(example_id) )
		if example is None:
			self.error(404)
		else:
			self.respond(example.to_dict(), cache_life=60*60) # cache for 1 hour

class RawValueHandler(BaseHandler):
	def get(self, example_id):
		example = Example.get_by_id( int(example_id) )
		if example is None:
			self.error(404)
		else:
			self.respond(example.value, content_type='text/plain', cache_life=60*60)



routes = [
	(r'/example/'         , CreateExampleHandler),
	(r'/example/(\d+)'    , ExampleHandler      ),
	(r'/example/(\d+)/raw', RawValueHandler     ),
]
