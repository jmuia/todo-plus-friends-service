#!/usr/bin/env python

from test_base import TestBase
import logging
import mock
from model.user import User


class TodoListTest(TestBase):
	def test_jws(self):

		user = self.auth_api_call('post', '/users/', {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME
		}).json
		assert user['id'] == self.USERNAME

		todo_list_name = 'Test List'
		todo_list = self.auth_api_call('post', '/users/'+self.USERNAME+'/todo-lists/', {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME,
					'name'     : todo_list_name
		}).json
		assert todo_list['name'] == todo_list_name

		todo_list = self.auth_api_call('get', '/users/'+self.USERNAME+'/todo-lists/'+str(todo_list['id']), {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME
		}).json
		assert todo_list['name'] == todo_list_name

	# TODO def test_mocks(self):

