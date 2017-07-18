#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os.path

def ole2rtf(oleFilename):
    targetFile = os.path.splitext(oleFilename)[0] + ".rtf"
    fileContent = open(oleFilename, "rb").read()
    outFile = open(targetFile, "wb")
    outFile.write("{\\rtf1\\ansi\\deff3\\adeflang1025\n")
    outFile.write(fileContent)
    outFile.write("\n}")
    outFile.close()
    return [targetFile]
#    outFile = open()