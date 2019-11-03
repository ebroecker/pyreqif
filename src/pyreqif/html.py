#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import io
import os.path
import pyreqif.ole2rtf
from lxml import etree
import sys
#reload(sys)
#sys.setdefaultencoding('utf8')

def create_html(item, cols, depth, basepath):
    tempReq = {}
    htmlOutput = "<td>"
    htmlOutput += "+" * depth

    for col, value in item.items():
        if col not in cols:
            continue
        if type(value) is not bytes:
            value = value.encode("utf8")
        if value is not None:
            if b"<" in value and b">" in value:
                try:
                    tree = etree.parse(io.BytesIO(value))
                    root = tree.getroot()
                    for element in root.iter("object"):
                        rtfFilename = os.path.join(basepath, element.attrib["data"])
                        files = pyreqif.ole2rtf.ole2rtf(rtfFilename)
                        if rtfFilename.endswith("ole"):
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
                            else:
                                element.tag = "div"
                        else:
                            element.tag = "div"
                    value = etree.tostring(root)
                    value = value.encode("utf8")
                except:
                    pass
        tempReq[col] = value
    for col in cols:
        htmlOutput += "<td>"
        if col in tempReq:
            if tempReq[col] is not None:
                htmlOutput += tempReq[col].decode("utf8")
            else:
                htmlOutput += ""
    htmlOutput += "</tr><tr>"
    return htmlOutput


def dump(myDoc, outfile, basepath = None):
    if basepath is None:
        basepath = os.path.dirname(outfile)

    for specification in myDoc.specificationList:
        htmlOutput = u"<table border=1><tr><td>"
        cols = myDoc.fields

        colNr = 0
        for col in cols:
            htmlOutput += u"<td>" + col
            colNr += 1

        htmlOutput += u"</tr><tr>"

        for child in myDoc.hierarchy:
            for item, depth in myDoc.hierach_iterator(child, cols):
                htmlOutput += create_html(item, cols, depth, basepath)
#        for req in specification:
#            reqObj = myDoc.getReqById(req)
#            htmlOutput += create_html(myDoc.flatReq(reqObj, html=True), cols, 0, basepath)
        htmlOutput += "</table>"
    fp = open(outfile, "wb")
    fp.write(bytes(htmlOutput, "utf8"))
    fp.close()
