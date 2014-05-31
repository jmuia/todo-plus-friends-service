#!/usr/bin/env python

from lib.utils import BaseHandler



class WarmupHandler(BaseHandler):
	def get(self):
		# This get's called by AppEngine when your server starts up.
		# Add any necessary startup logic here.
		self.respond('Hello, world!')



routes = [
	(r'/_ah/warmup', WarmupHandler),
]
