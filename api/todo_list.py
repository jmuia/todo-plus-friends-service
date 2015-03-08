#!/usr/bin/env python

from lib.utils import BaseHandler

from model.todo_list import TodoList

from google.appengine.ext import ndb


class CreateTodoListHandler(BaseHandler):

    def post(self):
        # TODO - hostname verification

        # self.username defined by verified jws data
        if self.username is None:
            self.respond_error(400)

        elif self.auth_params is None:
            self.respond_error(400)

        elif self.auth_params.get('name') is None:
            self.respond_error(400)

        else:
            key = ndb.Key('User', self.username)
            user = key.get()

            if user is None:
                self.respond_error(404)
            else:

                todo_list = TodoList(name=self.auth_params.get('name'),
                                     items=self.auth_params.get('items') or [])
                todo_key = todo_list.put()
                user.todo_lists.append(todo_key)
                user.put()

                self.respond(todo_list)


class TodoListHandler(BaseHandler):

    def get(self, entity_id):

        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)

        if self.username is None:
            self.respond_error(400)

        elif not entity_id:
            self.respond_error(400)

        else:
            key = ndb.Key('User', self.username)
            user = key.get()

            if user is None:
                self.respond_error(404)
            else:
                todo_list = TodoList.get_by_id(entity_id)

                if todo_list is None:
                    self.respond_error(404)
                elif todo_list.key not in user.todo_lists:
                    self.respond_error(403)
                else:
                    self.respond(todo_list)

    def put(self, entity_id):

        if entity_id and entity_id.isdigit():
            entity_id = int(entity_id)

        if self.username is None:
            self.respond_error(400)

        elif self.auth_params is None:
            self.respond_error(400)

        elif self.auth_params.get('name') is None:
            self.respond_error(400)

        elif not entity_id:
            self.respond_error(400)

        else:
            key = ndb.Key('User', self.username)
            user = key.get()

            if user is None:
                self.respond_error(404)
            else:
                todo_list = TodoList.get_by_id(entity_id)

                if todo_list is None:
                    self.respond_error(404)
                elif todo_list.key not in user.todo_lists:
                    self.respond_error(403)
                else:
                    todo_list.name = self.auth_params.get('name')
                    todo_list.items = self.auth_params.get('items') or []
                    todo_list.put()
                    self.respond(todo_list)

routes = [
    (r'/todo-lists',       CreateTodoListHandler),
    (r'/todo-lists/(\d*)', TodoListHandler)
]
