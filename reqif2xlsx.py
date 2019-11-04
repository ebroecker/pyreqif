#!/usr/bin/env python3
import pyreqif.rif
import pyreqif.xlsx
import sys
import os

def main():
    doc = pyreqif.rif.load(sys.argv[1])
    pyreqif.xlsx.dump(doc,sys.argv[2], os.path.dirname(sys.argv[1]))

main()
