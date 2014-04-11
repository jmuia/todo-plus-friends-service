#!/usr/bin/env python

from test_base import TestBase



class RestExampleTest(TestBase):
	def test_hello_world(self):
		value  = 'foobar'
		value2 = 'foo2'

		rest_example = self.api_call('post', '/rest-example/', { 'value': value }).json
		assert rest_example['value'] == value
		rest_example = self.api_call('get', '/rest-example/%s' % rest_example['id']).json
		assert rest_example['value'] == value

		rest_example = self.api_call('patch', '/rest-example/%s' % rest_example['id'], { 'value': value2 }).json
		assert rest_example['value'] == value2
		rest_example = self.api_call('get', '/rest-example/%s' % rest_example['id']).json
		assert rest_example['value'] == value2

		rest_example = self.api_call('delete', '/rest-example/%s' % rest_example['id']).json
		assert rest_example['value'] == value2
		self.api_call('get', '/rest-example/%s' % rest_example['id'], status=404)
