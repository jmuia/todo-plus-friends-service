#!/usr/bin/env python

from datetime import datetime, timedelta
from json     import loads as json_parse
from urllib   import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

from lib.utils import DEBUG



GRACE_PERIOD = 300 # seconds
ALGORITHMS   = {
	'RS256' : 'SHA256withRSA',
	'RS384' : 'SHA384withRSA',
	'RS512' : 'SHA512withRSA',
}
VERIFY_URL   = 'https://auth.kik.com/verification/v1/check?'



#TODO: cron to cleanup old sessions
class Session(ndb.Model):
	created_at = ndb.DateTimeProperty(auto_now_add=True)
	username = ndb.StringProperty(indexed=False)
	hostname = ndb.StringProperty(indexed=False)



def get_verified_data(jws, expected=None, session_token=None):
	headers = json_parse(get_jws_part(jws, 0))
	username = headers['kikUsr'  ].lower()
	hostname = headers['kikCrdDm'].split('/')[0]
	payload  = get_jws_part(jws, 1)
	if headers.get('kikDbg') and DEBUG:
		debug = True
	else:
		debug = False

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
		try:
			verify_jws(jws, username, hostname, debug)
		except:
			return None, None, None, None
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
