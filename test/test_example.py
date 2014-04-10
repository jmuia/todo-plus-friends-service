#!/usr/bin/env python

from test_base import *



class ExampleTest(TestBase):
	def test_hello_world(self):
		value = 'foobar'

		example = self.api_call('post', '/example/', { 'value': value }).json
		assert example['value'] == value

		example = self.api_call('get', '/example/%s' % example['id']).json
		assert example['value'] == value

		response = self.api_call('get', '/example/%s/raw' % example['id'])
		assert response.body == value
