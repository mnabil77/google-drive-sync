#!/usr/bin/env python

"""GoogleDriveSync.py: Service for logging information"""

__author__      = "Pavel Hosek"
__copyright__   = "Copyright 2014, Pavel Hosek"
__license__ 	= "Public Domain"
__version__ 	= "1.0"

import sys

class LogService(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def close(self):
    	self.log.close()