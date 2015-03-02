#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel
from model.user import User
from model.todo_item import TodoItem


class TodoList(BaseModel):
    name = ndb.StringProperty(required=True)
    items = ndb.KeyProperty(TodoItem, repeated=True)

    @classmethod
    def users(cls):
        return User.query(User.todo_lists == cls.id)

    @classmethod
    def create_first_todo_list(cls):
        todo_list = TodoList()
        todo_list.name = "My First Todo List"
        todo_list.items = [TodoItem(description="Cross off my first todo item").put()]
        return todo_list.put()
