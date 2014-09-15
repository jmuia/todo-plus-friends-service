import logging
from base64 import b64encode
from json   import dumps as json_stringify
from math   import ceil
from Queue  import Queue, Empty as EmptyQueueException, Full as FullQueueException
from time   import time

from google.appengine.api import urlfetch
from google.appengine.api import runtime

MiXPANEL_TOKEN      = 'PUT_YOUR_TOKEN_HERE'
API_URL             = 'http://api.mixpanel.com/track/'
MAX_BATCH_SIZE      = 50
SMART_FLUSH_TIMEOUT = 5 # seconds
DONT_FLUSH_QUEUE    = False

queue      = Queue()
last_flush = None
runtime.set_shutdown_hook(flush)



# This is meant to be called by test_base only.
def get_queue():
	size   = queue.qsize()
	events = []
	for i in range(size):
		try:
			events.append( queue.get_nowait() )
			queue.task_done()
		except EmptyQueueException:
			break
	return events

def clear():
	queue = Queue()

def track(distinct_id, event_name, properties=None):
	if properties is None:
		properties = {}
	properties['token'      ] = MiXPANEL_TOKEN
	properties['distinct_id'] = distinct_id
	event = {
		'event'      : event_name,
		'properties' : properties,
	}
	if not last_flush:
		last_flush = time()
	try:
		queue.put_nowait(event)
	except FullQueueException:
		logging.error('mixpanel queue is full, failed to log event=%s' % json_stringify(event))

def smart_flush():
	size = queue.qsize()
	if size > 0 and (size >= MAX_BATCH_SIZE or (last_flush and time()-last_flush >= SMART_FLUSH_TIMEOUT)):
		flush(max_batches=ceil(float(size)/MAX_BATCH_SIZE))

def flush(max_batches=10):
	last_flush = time()

	if DONT_FLUSH_QUEUE:
		return

	size = min(queue.qsize(), max_batches*MAX_BATCH_SIZE)
	if not size:
		return

	events = []
	for index in range(size):
		try:
			events.append( queue.get_nowait() )
			queue.task_done()
		except EmptyQueueException:
			break
	if not events:
		return

	# Do not send metrics events in debug mode
	from lib.utils import DEBUG
	if DEBUG:
		return

	rpcs = []
	for index in range(0, len(events), MAX_BATCH_SIZE):
		batch = events[index:index+MAX_BATCH_SIZE]
		data  = 'data=' + b64encode(json_stringify(batch))
		rpc   = urlfetch.create_rpc()
		try:
			urlfetch.make_fetch_call(
				rpc,
				API_URL,
				method  = 'POST',
				headers = { 'Content-Type' : 'application/x-www-form-urlencoded' },
				payload = data,
			)
			rpcs.append(rpc)
		except Exception as e:
			logging.error('failed to trigger urlfetch')
			logging.exception(e)

	for rpc in rpcs:
		try:
			rpc.wait()
		except Exception as e:
			logging.error('failed to resolve urlfetch')
			logging.exception(e)
