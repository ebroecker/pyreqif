#!/usr/bin/env python2
import os.path
from oletools import rtfobj

def extractOleData(rtfFilename):
    createdFiles = []
    rtfData = open(rtfFilename, 'rb').read()
    rtfp = rtfobj.RtfObjParser(rtfData)
    rtfp.parse()
    for obj in rtfp.objects:
        if 'Acro' in obj.class_name: # PDF
            outfileName = os.path.splitext(rtfFilename)[0] + ".pdf"
            outfileData = obj.oledata[obj.oledata.find("%PDF-1."):]

        elif 'Package' == obj.class_name:
            outfileName = os.path.join(os.path.dirname(rtfFilename), obj.filename)
            outfileData = obj.olepkgdata
        else:
            pass
        createdFiles.append(outfileName)

        outfile = open(outfileName, "wb")
        outfile.write(outfileData)
        outfile.close()

    return createdFiles
