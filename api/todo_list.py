#!/usr/bin/env python

from lib.utils import BaseHandler

from model.todo_list import TodoList
from model.user import User

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

                users_param = self.auth_params.get('users')
                if users_param is not None:
                    user_keys = users_param_to_keys(users_param)
                    if user.key not in user_keys:
                        user_keys.append(user.key)
                else:
                    user_keys = [user.key]

                todo_list = TodoList(name=self.auth_params.get('name'),
                                     items=self.auth_params.get('items') or [],
                                     users=user_keys)

                todo_list.put()
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
                elif user.key not in todo_list.users:
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
                elif user.key not in todo_list.users:
                    self.respond_error(403)
                else:

                    users_param = self.auth_params.get('users')
                    if users_param is not None:
                        user_keys = users_param_to_keys(users_param)
                        if user.key not in user_keys:
                            user_keys.append(user.key)
                    else:
                        user_keys = [user.key]

                    todo_list.name = self.auth_params.get('name')
                    todo_list.items = self.auth_params.get('items') or []
                    todo_list.users = user_keys
                    todo_list.put()
                    self.respond(todo_list)


def users_param_to_keys(params):
    keys = []
    for username in params:
        user = ndb.Key('User', username).get()
        if user is None:
            user = User(id=username)
            user.create_first_todo_list()
            key = user.put()
        else:
            key = user.key

        if key not in keys:
            keys.append(key)

    return keys

routes = [
    (r'/todo-lists',       CreateTodoListHandler),
    (r'/todo-lists/(\d*)', TodoListHandler)
]
