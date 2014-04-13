#!/usr/bin/env python

from test_base import TestBase



class AuthExampleTest(TestBase):
	def test_hello_world(self):
		value  = 'foobar'
		value2 = 'foo2'

		auth_example = self.auth_api_call('post', '/auth-example/', {
			'username' : self.USERNAME,
			'hostname' : self.HOSTNAME,
			'value'    : value,
		}).json
		assert auth_example['username'] == self.USERNAME
		assert auth_example['hostname'] == self.HOSTNAME
		assert auth_example['value'   ] == value

		self.auth_api_call('patch', '/auth-example/%s' % auth_example['id'], {
			'value' : value2,
		})
		auth_example = self.auth_api_call('get', '/auth-example/%s' % auth_example['id']).json
		assert auth_example['value'] == value2

		self.USERNAME = 'dan'
		self.auth_api_call('get', '/auth-example/%s' % auth_example['id'], status=403)
