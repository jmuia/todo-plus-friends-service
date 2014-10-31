#!/usr/bin/env python

import logging
from base64   import b64decode
from datetime import datetime, timedelta
from json     import loads as json_parse
from urllib   import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

from lib.utils     import DEBUG
from model.session import Session



VERIFY_URL   = 'https://auth.kik.com/verification/v1/check?'
TEST_USERS = [
	'kikteam',
	'dan',
	'mark',
]



def get_verified_data(jws, expected=None, session_token=None):
	headers = json_parse(get_jws_part(jws, 0))
	raw_username = headers['kikUsr']
	username = raw_username.lower()
	hostname = headers['kikCrdDm'].split('/')[0].lower()
	payload  = get_jws_part(jws, 1)

	if expected is not None and payload != expected:
		logging.info('jws, payload does not match expected value')
		raise Exception('payload does not match expected value')

	try:
		data = json_parse(payload)
	except:
		data = None

	try:
		session = ndb.Key(urlsafe=session_token).get()
	except Exception as e:
		session = None
	if session is None or not isinstance(session, Session) or session.username != username or session.hostname != hostname:
		session       = None
		session_token = None
		if username not in TEST_USERS:
			verify_jws(jws, raw_username, hostname, (headers.get('kikDbg') and DEBUG))
		elif not DEBUG:
			logging.info('jws, chrome user detected')
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
	)
	if result.status_code != 200:
		logging.info('jws, verification failed, status=%s' % result.status_code)
		raise Exception('verification failed, status=%s' % result.status_code)

def get_jws_part(jws, index):
	part = jws.split('.')[index]
	part += '===='
	return b64decode(part, '-_')
