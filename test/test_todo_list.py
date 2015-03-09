#!/usr/bin/env python

from test_base import TestBase
import mock
from model.user import User


class TodoListTest(TestBase):
	def test_jws(self):

		user = self.auth_api_call('post', '/users', {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME
		}).json
		assert user['id'] == self.USERNAME

		todo_list_name = 'Test List'
		todo_list = self.auth_api_call('post', '/todo-lists', {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME,
					'name'     : todo_list_name
		}).json
		assert todo_list['name'] == todo_list_name
		assert len(todo_list['users']) == 1
		assert len(todo_list['items']) == 0
		assert self.USERNAME in [ user['id'] for user in todo_list['users'] ]

		todo_list = self.auth_api_call('get', '/todo-lists/'+str(todo_list['id']), {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME
		}).json
		assert todo_list['name'] == todo_list_name
		assert len(todo_list['users']) == 1

		todo_list_name = 'Updated List'
		todo_list = self.auth_api_call('put', '/todo-lists/'+str(todo_list['id']), {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME,
					'name'     : todo_list_name
		}).json	
		assert todo_list['name'] == todo_list_name
		assert len(todo_list['users']) == 1
		assert self.USERNAME in [ user['id'] for user in todo_list['users'] ]

		users = ['test1', 'test2']
		todo_list = self.auth_api_call('put', '/todo-lists/'+str(todo_list['id']), {
					'username' : self.USERNAME,
					'hostname' : self.HOSTNAME,
					'name'     : todo_list_name,
					'users'    : users
		}).json	
		assert todo_list['name'] == todo_list_name
		assert len(todo_list['users']) == 3

		items = [
			{ "completed": True, "description": "test"},
			{ "completed": False, "description": "test2"},
		]
		todo_list = self.auth_api_call('put', '/todo-lists/'+str(todo_list['id']), {
			'username' : self.USERNAME,
			'hostname' : self.HOSTNAME,
			'name'     : todo_list_name,
			'items'    : items
		}).json
		assert len(todo_list['items']) == len(items)



	# TODO def test_mocks(self):

