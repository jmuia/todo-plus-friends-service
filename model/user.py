#!/usr/bin/env python

from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

from lib.utils import DEBUG



VERIFY_URL = 'https://auth.kik.com/verification/v1/check?'



def verify_user(signed_data, host, username=None, anonymous_id=None):
	if not signed_data:
		raise Exception('signed data was not provided')

	args = {}

	if (username is None) and (anonymous_id is None):
		raise Exception('either username or anonymous_id must be provided')

	if (username is not None) and (not username):
		raise Exception('either username or anonymous_id must be provided')
	else:
		args['u'] = username

	if (anonymous_id is not None) and (not anonymous_id):
		raise Exception('either username or anonymous_id must be provided')
	else:
		args['a'] = anonymous_id

	if not host:
		raise Exception('host was not provided')
	else:
		args['d'] = host

	if DEBUG:
		args['debug'] = 'true'

	result = urlfetch.fetch(VERIFY_URL+urlencode(args),
		validate_certificate = True        ,
		deadline             = 10          ,
		follow_redirects     = True        ,
		method               = 'POST'      ,
		payload              = signed_data ,
		allow_truncated      = True
	)
	if result.status_code != 200:
		raise Exception('auth verification request failed, http_status=%s' % result.status_code)

	return result.content.strip()
