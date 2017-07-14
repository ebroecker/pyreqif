#!/usr/bin/env python
import pyreqif.reqif
import pyreqif.html
import sys
import os

def main():
    doc = pyreqif.reqif.load(sys.argv[1])
    pyreqif.html.dump(doc,sys.argv[2], os.path.dirname(sys.argv[1]))

main()