#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import io
import os.path
import ole2rtf
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def dump(myDoc, outfile, basepath = None):
    if basepath is None:
        basepath = os.path.dirname(outfile)

    for specification in myDoc.specificationList:
        htmlOutput = u"<table border=1><tr>"
        cols = myDoc.fields

        colNr = 0
        for col in cols:
            htmlOutput += u"<td>" + col
            colNr += 1

        htmlOutput += u"</tr><tr>"

        for req in specification:
            reqObj = myDoc.getReqById(req)
            tempReq ={}
            for col,value in myDoc.flatReq(reqObj, html=True).iteritems():
                if value is not None:
                    if "<" in value:
                        try:
                            tree = etree.parse(io.BytesIO(value))
                            root = tree.getroot()
                            for element in root.iter("object"):
                                rtfFilename = os.path.join(basepath, element.attrib["data"])
                                files = ole2rtf.ole2rtf(rtfFilename)
                                if len(files) > 0:
                                    if "name" in element.attrib:
                                        name = element.attrib["name"]
                                    else:
                                        name = ""

                                    for key in element.attrib:
                                        del element.attrib[key]
                                    element.tag = "a"
                                    element.set("href", files[0])
                                    element.text = name
                                    imgElement = etree.Element("img")
                                    imgElement.set("src", os.path.splitext(files[0])[0] + ".png")
                                    element.append(imgElement)

                            value = etree.tostring(root)
                        except:
                            pass
                tempReq[col] = value
            for col in cols:
                htmlOutput += "<td>"
                if col in tempReq:
                    if tempReq[col] is not None:
                        htmlOutput += tempReq[col]
                    else:
                        htmlOutput += ""
            htmlOutput += "</tr><tr>"
        htmlOutput += "</table>"
    fp = open(outfile, "wb")
    fp.write(htmlOutput)
    fp.close()
