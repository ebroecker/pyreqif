#!/usr/bin/env python3
import pyreqif.rif
import pyreqif.html
import sys
import os

def main():
    doc = pyreqif.rif.load(sys.argv[1])
    pyreqif.html.dump(doc,sys.argv[2], os.path.dirname(sys.argv[1]))

main()
