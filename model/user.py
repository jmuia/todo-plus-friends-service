#!/usr/bin/env python

from model.todo_list import TodoList

from lib.utils import BaseModel


class User(BaseModel):
    # id = a_username
    def todo_lists(self):
        return TodoList.query(TodoList.users == self.key).fetch()

    def create_first_todo_list(self):
        todo_list = TodoList()
        todo_list.name = "My First Todo List"
        todo_list.items = [{"completed":False, "description":"something to do"}]
        todo_list.users = [self.key]
        return todo_list.put()