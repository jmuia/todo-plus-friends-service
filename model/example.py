#!/usr/bin/env python

from google.appengine.ext import ndb



class Example(ndb.Model):
	value = ndb.StringProperty()
