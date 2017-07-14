#!/usr/bin/env python2
import pyreqif.reqif
import pyreqif.xlsx
import sys
import os

def main():
    doc = pyreqif.reqif.load(sys.argv[1])
    pyreqif.xlsx.dump(doc,sys.argv[2], os.path.dirname(sys.argv[1]))

main()