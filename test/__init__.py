#!/usr/bin/env python

import sys
import os

SDK_GUESSES=['/usr/local/google_appengine']

sdk_path = next((guess for guess in SDK_GUESSES if os.path.isdir(guess)), None)
if sdk_path is None:
    raise Exception("""
I couldn't find your app engine SDK. Please figure out where it is, and add
it to SDK_GUESSES in test/__init__.py for posterity :)
""")

try:
    import webtest
except:
    raise Exception("""
could not import webtest. Maybe try:
 $ sudo easy_install webtest
or something to that effect?
""")

sys.path.insert(0, sdk_path)
import dev_appserver
dev_appserver.fix_sys_path()
