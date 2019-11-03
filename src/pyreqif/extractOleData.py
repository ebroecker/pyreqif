#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os.path
from oletools import rtfobj

def extractOleData(rtfFilename):
    createdFiles = []
    rtfData = open(rtfFilename, 'rb').read()
    rtfp = rtfobj.RtfObjParser(rtfData)
    rtfp.parse()
    for obj in rtfp.objects:
        if b'Acro' in obj.class_name: # PDF
            outfileName = os.path.splitext(rtfFilename)[0] + ".pdf"
            outfileData = obj.oledata[obj.oledata.find(b"%PDF-1."):]

        elif b'Package' == obj.class_name:
            outfileName = os.path.join(os.path.dirname(rtfFilename), obj.filename)
            outfileData = obj.olepkgdata
        elif b'Word' in obj.class_name:
#            if "PK\03\04" in obj.oledata:
#                outfileData = obj.oledata[obj.oledata.find("PK\03\04"):]
#                outfileName = os.path.splitext(rtfFilename)[0] + ".docx"
#            else:
            outfileName = os.path.splitext(rtfFilename)[0] + ".doc"
            outfileData = obj.oledata
        elif b'Excel' in obj.class_name:
            if b"PK\03\04" in obj.oledata:
                outfileData = obj.oledata[obj.oledata.find("PK\03\04"):]
                outfileName = os.path.splitext(rtfFilename)[0] + ".xlsx"
            else:
                outfileData = obj.oledata
                outfileName = os.path.splitext(rtfFilename)[0] + ".xls"
        else:
            pass
        createdFiles.append(outfileName)

        outfile = open(outfileName, "wb")
        outfile.write(outfileData)
        outfile.close()

    return createdFiles
