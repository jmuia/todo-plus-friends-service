#!/usr/bin/env python

import os
import sys


import subprocess
import tempfile

SDK_GUESSES=['/usr/local/google_appengine']
with tempfile.NamedTemporaryFile() as f:
	f.write('''
		bin_path="`which dev_appserver.py`"
		if [ -n "${bin_path}" ] ; then
			real_path="`readlink ${bin_path}`"
			if [ "`echo ${real_path} | cut -c1`" = "/" ] ; then
				abs_path="${real_path}"
			else
				abs_path="`dirname ${bin_path}`/${real_path}"
			fi
			dir_path="`dirname ${abs_path}`"
			echo "${dir_path}"
		fi
	''')
	f.flush()
	sdk_path = subprocess.check_output(['/bin/bash', f.name]).strip()
	if sdk_path:
		SDK_GUESSES.append(sdk_path)

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
