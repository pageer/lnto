#!/usr/bin/env python

import os

print "Content-type: text/html"
print ""
print "SECRET_KEY = '" + repr(os.urandom(24)) + "'"