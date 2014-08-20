import logging
from base64 import b64encode
from json   import dumps as json_stringify
from Queue  import Queue, Empty as EmptyQueueException, Full as FullQueueException

from google.appengine.api import urlfetch

MiXPANEL_TOKEN   = 'PUT_YOUR_TOKEN_HERE'
API_URL          = 'http://api.mixpanel.com/track/'
MAX_BATCH_SIZE   = 50
DONT_FLUSH_QUEUE = False

queue = Queue()



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
	try:
		queue.put_nowait(event)
	except FullQueueException:
		logging.error('mixpanel queue is full, failed to log event=%s' % json_stringify(event))

def flush():
	if DONT_FLUSH_QUEUE:
		return

	size = queue.qsize()
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
	from utils import DEBUG
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
