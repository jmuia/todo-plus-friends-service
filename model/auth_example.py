#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel



class AuthExample(BaseModel):
	username = ndb.StringProperty(required=True)
	hostname = ndb.StringProperty(required=True)
	value    = ndb.StringProperty()
