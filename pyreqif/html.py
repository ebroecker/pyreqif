#!/usr/bin/env python2

import io
import os.path
import extractOleData
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def dump(myDoc, outfile, basepath = None):
    if basepath is None:
        basepath = os.path.dirname(outfile)

    for specification in myDoc.specificationList:
        htmlOutput = u"<table><tr>"
        row = 0
        cols = []
        for req in specification:
            reqObj = myDoc.getReqById(req)
            for col in myDoc.flatReq(reqObj, html=True):
                if col  not in cols:
                    cols.append(col)

        colNr = 0
        for col in cols:
            htmlOutput += u"<td>" + col
            colNr += 1

        htmlOutput += u"</tr><tr>"

        for req in specification:
            row += 1
            reqObj = myDoc.getReqById(req)
            for col,value in myDoc.flatReq(reqObj, html=True).iteritems():
                if value is not None:
                    if "<" in value:
                        try:
                            tree = etree.parse(io.BytesIO(value))
                            root = tree.getroot()
                            for element in root.iter("object"):
                                rtfFilename = os.path.join(basepath, element.attrib["data"])
                                files = extractOleData.extractOleData(rtfFilename)
                                if len(files) > 0:
                                    name = element.attrib["name"]

                                    for key in element.attrib:
                                        del element.attrib[key]
                                    element.tag = "a"
                                    element.set("href", files[0])
                                    element.text = name
                            value = etree.tostring(root)
                        except:
                            pass
                    htmlOutput += "<td>" + value
            htmlOutput += "</tr><tr>"
        htmlOutput += "</table>"
    fp = open(outfile, "wb")
    fp.write(htmlOutput)
    fp.close()
