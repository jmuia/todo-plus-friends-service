#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel



class RestExample(BaseModel):
	value = ndb.StringProperty()
