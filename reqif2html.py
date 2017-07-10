#!/usr/bin/env python
import pyreqif.reqif
import pyreqif.html
import sys

doc = pyreqif.reqif.load(sys.argv[1])
pyreqif.html.dump(doc,sys.argv[2])
