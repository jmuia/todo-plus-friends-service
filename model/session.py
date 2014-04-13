#!/usr/bin/env python

from datetime import timedelta

from google.appengine.ext import ndb

from lib.utils import BaseModel

MAX_AGE = timedelta(hours=6)



class Session(BaseModel):
	created_at = ndb.DateTimeProperty(auto_now_add=True)
	username = ndb.StringProperty(indexed=False)
	hostname = ndb.StringProperty(indexed=False)
