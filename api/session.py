#!/usr/bin/env python

import logging

from google.appengine.ext import ndb

from lib.utils     import BaseHandler, admin_only
from model.session import Session, MAX_AGE



class CleanupSessionsHandler(BaseHandler):
	@admin_only
	def get(self):
		cutoff = datetime.utcnow() - MAX_AGE
		sessions = Session.query(Session.created_at < cutoff).fetch(200, keys_only=True)
		if len(sessions) > 0:
			ndb.delete_multi(sessions)
		logging.info('%s sessions cleared' % len(sessions))



routes = [
	(r'/session/cleanup', CleanupSessionsHandler),
]
