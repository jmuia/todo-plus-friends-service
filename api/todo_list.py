#!/usr/bin/env python

from lib.utils import BaseHandler

from model.user import User
from model.todo_list import TodoList

from google.appengine.ext import ndb
import logging


class CreateTodoListHandler(BaseHandler):
    def post(self, username):
        # TODO - hostname verification

        # self.username defined by verified jws data
        if self.username is None:
            self.respond_error(400)


        elif self.auth_params is None:
            self.respond_error(400)

        elif self.auth_params.get('name') is None:
            self.respond_error(400)

        elif self.username != username:
            self.respond_error(403)
       
        else:
            key = ndb.Key('User', self.username)
            user = key.get()

            if user is None:
                self.respond_error(404)
            else:
                todo_list = TodoList(name=self.auth_params.get('name'))
                todo_list.put()
                self.respond(todo_list)


class TodoListHandler(BaseHandler):
    def get(self, username, entity_id):

        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)
        
        if self.username is None:
            self.respond_error(400)

        elif not entity_id:
            self.respond_error(400)

        elif self.username != username:
            self.respond_error(403)

        else:
            key = ndb.Key('User', username)
            user = key.get()
            
            if user is None:
                self.respond_error(404)
            else:
                todo_list = TodoList.get_by_id(entity_id)

                if todo_list is None:
                    self.respond_error(404)
                else:
                    self.respond(todo_list)

routes = [
    (r'/users/(\w+)/todo-lists/'     , CreateTodoListHandler),
    (r'/users/(\w+)/todo-lists/(\d*)', TodoListHandler      ),
]

