#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel



class Example(BaseModel):
	value = ndb.StringProperty()
