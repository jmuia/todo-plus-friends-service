#!/usr/bin/env python

from google.appengine.ext import ndb

from lib.utils import BaseModel
from model.example import Example



class RestExample(BaseModel):
	value    = ndb.StringProperty()
	examples = ndb.KeyProperty(Example, repeated=True)
