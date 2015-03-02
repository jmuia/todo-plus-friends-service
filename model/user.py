#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel


class User(BaseModel):
    # id = a_username
    todo_lists = ndb.KeyProperty(kind='TodoList', repeated=True, indexed=False)
