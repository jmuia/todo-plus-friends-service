#!/usr/bin/env python

import os
import base64
import logging
import urlparse
import unittest

from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
import webapp2
import webtest

from app import app



class TestBase(unittest.TestCase):
	def setUp(self):
		root = os.path.dirname('..')
		self.policy  = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1.0)
		self.app     = app
		self.testapp = webtest.TestApp(self.app)
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_taskqueue_stub(root_path=root)
		self.testbed.init_memcache_stub()
		self.testbed.init_datastore_v3_stub(root_path=root, consistency_policy=self.policy)
		self.testbed.init_urlfetch_stub()
		self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

	def tearDown(self):
		self.testbed.deactivate()

	def get_tasks(self, queue='default'):
		return self.taskqueue_stub.GetTasks(queue)

	def get_task_params(self, queue='default'):
		return [dict(urlparse.parse_qsl(base64.b64decode(t["body"]))) for t in self.get_tasks(queue)]

	def execute_tasks(self, queue='default'):
		tasks =  self.get_tasks(queue)
		responses = []
		for task in tasks:
			params = base64.b64decode(task['body'])
			response = self.testapp.post(task['url'], params)
			responses.append(response)
		return tasks, responses

	def api_call(self, method, resource, data=None, status=200, headers={}):
		method  = method.lower()
		is_json = False

		if data and (type(data) is dict) and (method in ['post', 'put']):
			is_json = True

		if is_json:
			func = getattr(self.testapp, method.lower()+'_json')
		else:
			func = getattr(self.testapp, method.lower())

		return func(resource, params=data, status=status, headers=headers)
