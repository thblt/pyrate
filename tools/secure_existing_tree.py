#!/usr/bin/env python

import os
from werkzeug import secure_filename

def secure(path):
	for f in os.listdir(path):
		canonical = os.path.join(path, f)
		secureCanonical = os.path.join(path, secure_filename(f))
		print("{0} => {1}" .format(canonical, secureCanonical))
		os.renames(canonical, secureCanonical)

		if os.path.isdir(canonical): 
			secure(canonical)

if __name__=='__main__':
	import sys
	secure(sys.argv[-1])
