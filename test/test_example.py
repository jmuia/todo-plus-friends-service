#!/usr/bin/env python

from test_base import *



class ExampleTest(TestBase):
	def test_hello_world(self):
		value = 'foobar'

		response = self.api_call('post', '/example/', { 'value': value })
		assert response.status_int == 200
		assert 'example_id' in response.json

		response = self.api_call('get', '/example/%s' % response.json['example_id'])
		assert response.json['value'] == value
