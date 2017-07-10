#!/usr/bin/env python2
import pyreqif.reqif
import pyreqif.xlsx
import sys

doc = pyreqif.reqif.load(sys.argv[1])
pyreqif.xlsx.dump(doc,sys.argv[2])
