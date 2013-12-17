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
			self.respond( example.to_dict() )



routes = [
	(r'/example/?'    , CreateExampleHandler),
	(r'/example/(\d+)', ExampleHandler      ),
]
