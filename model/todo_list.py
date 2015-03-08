#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel
from model.user import User
import jsonschema


class TodoList(BaseModel):
    def validate_items(prop, value):
        if value is not None:
            schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "completed": {"type": "boolean"},
                        "description": {"type": "string"}
                    }
                }
            }
            jsonschema.validate(value, schema)

    name = ndb.StringProperty(required=True)
    items = ndb.JsonProperty(indexed=False, validator=validate_items)

    def users(self):
        return User.query(User.todo_lists == self.key().id())

    @classmethod
    def create_first_todo_list(cls):
        todo_list = TodoList()
        todo_list.name = "My First Todo List"
        todo_list.items = [{"completed":False, "description":"something to do"}]
        return todo_list.put()
