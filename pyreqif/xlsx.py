#!/usr/bin/env python2
import io
import os.path
from lxml import etree
import extractOleData
import xlsxwriter

def dump(myDoc, outfile, basepath = None):
    if basepath is None:
        basepath = os.path.dirname(outfile)
    workbook = xlsxwriter.Workbook(outfile)

    for specification in myDoc.specificationList:
        if len(specification.name) > 31:
            worksheet = workbook.add_worksheet(specification.name[:31])
        else:
            worksheet = workbook.add_worksheet(specification.name)
        row = 0
        cols = myDoc.fields

        colNr = 0
        for col in cols:
            worksheet.write(0, colNr, col)
            colNr += 1

        for req in specification:
            files = []
            row += 1
            reqObj = myDoc.getReqById(req)
            for col,value in myDoc.flatReq(reqObj, html=True).iteritems():
                if value is not None:
                    if "<" in value:
                        tree = etree.parse(io.BytesIO(value))
                        root = tree.getroot()
                        for element in root.iter("object"):
                            rtfFilename = os.path.join(basepath, element.attrib["data"])
                            files = extractOleData.extractOleData(rtfFilename)
                            name = element.attrib["name"]

                            if len(files) > 0:
                                for key in element.attrib:
                                    del element.attrib[key]
                                element.tag = "a"
                                element.set("href", files[0])
                                element.text = "linked file: " + files[0]
                        value = "".join(root.itertext())
                worksheet.write(row, cols.index(col), value)
                if len(files) > 0:
                    worksheet.insert_image(row, cols.index(col), os.path.splitext(files[0])[0] + ".png")
    workbook.close()
