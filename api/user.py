#!/usr/bin/env python

from lib.utils import BaseHandler

from model.user import User
from model.todo_list import TodoList

from google.appengine.ext import ndb
from google.appengine.ext.ndb import metadata
import logging


class CreateUserHandler(BaseHandler):
	def post(self):
		# TODO - hostname verification

		# self.username defined by verified jws data
		if self.username is None:
			self.respond_error(400)
		else:
			key = ndb.Key('User', self.username)
			user = key.get()

			# If the user does not yet exist, create a new user,
			# and create a default first todo list
			if user is None:
				user = User(id=self.username)
				user.todo_lists = [TodoList.create_first_todo_list()]
				user.put()

			self.respond(user)


class UserHandler(BaseHandler):
	def get(self, username):

		if self.username is None or not username:
			self.respond_error(400)

		elif self.username != username:
			self.respond_error(403)

		else:
			key = ndb.Key('User', username)
			user = key.get()
			if user is None:
				self.respond_error(404)
			else:
				self.respond(user)

routes = [
	(r'/users'        , CreateUserHandler),
	(r'/users/(\w*)'  , UserHandler      ),
]
