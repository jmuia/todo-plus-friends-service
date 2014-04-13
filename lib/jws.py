#!/usr/bin/env python

import logging
from datetime import datetime, timedelta
from json     import loads as json_parse
from urllib   import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

from lib.utils     import DEBUG
from model.session import Session



VERIFY_URL   = 'https://auth.kik.com/verification/v1/check?'
CHROME_USERS = [
	'kikteam',
]



def get_verified_data(jws, expected=None, session_token=None):
	headers = json_parse(get_jws_part(jws, 0))
	username = headers['kikUsr'  ].lower()
	hostname = headers['kikCrdDm'].split('/')[0]
	payload  = get_jws_part(jws, 1)

	if expected is not None and payload != expected:
		raise Exception('payload does not match expected value')

	try:
		data = json_parse(payload)
	except:
		data = None

	session = ndb.Key(urlsafe=session_token).get()
	if session is None or not isinstance(session, Session) or session.username != username or session.hostname != hostname:
		session       = None
		session_token = None
		if username not in CHROME_USERS:
			verify_jws(jws, username, hostname, (headers.get('kikDbg') and DEBUG))
		elif not DEBUG:
			raise Exception('chrome user detected')
		try:
			session = Session(username=username, hostname=hostname)
			session.put()
			session_token = session.key.urlsafe()
		except:
			pass
	return username, hostname, data, session_token

def verify_jws(jws, username, hostname, debug=False):
	args = {
		'u' : username,
		'd' : hostname,
	}
	if debug:
		args['debug'] = 'true'

	result = urlfetch.fetch(VERIFY_URL+urlencode(args),
		deadline             = 10     ,
		follow_redirects     = True   ,
		method               = 'POST' ,
		payload              = jws    ,
		allow_truncated      = True
	)
	if result.status_code != 200:
		raise Exception('verification failed, status=%s' % result.status_code)

def get_jws_part(jws, index):
	part = jws.split('.')[index]
	mod  = len(part) % 4
	if mod == 2:
		part += '=='
	elif mod == 3:
		part += '='
	return part.decode('base64')