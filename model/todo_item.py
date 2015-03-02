#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel


class TodoItem(BaseModel):
    completed = ndb.BooleanProperty(default=False, required=True)
    description = ndb.StringProperty(required=True)
