#!/usr/bin/env python
import pyreqif.rif
import pyreqif.reqif
import sys
import os


def main():
    doc = pyreqif.rif.load(sys.argv[1])
    f = open(sys.argv[2], "w")
    pyreqif.reqif.dump(doc, f)


main()
