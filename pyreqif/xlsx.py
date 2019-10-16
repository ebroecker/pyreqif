#!/usr/bin/env python2
import io
import os.path
from lxml import etree
import extractOleData
import xlsxwriter



def workOnHierarch(asd, row=0, deepth = 0, cols=None, worksheet = None):
    files = []
    for col, value in asd.items():
        if value is not None:
            if "<" in value and ">" in value:
                try:
                    tree = etree.parse(io.BytesIO(value))
                    root = tree.getroot()
                    for element in root.iter("object"):
                        rtfFilename = os.path.join(basepath, element.attrib["data"])
                        files = extractOleData.extractOleData(rtfFilename)
                        # name = element.attrib["name"]

                        if len(files) > 0:
                            for key in element.attrib:
                                del element.attrib[key]
                            element.tag = "a"
                            element.set("href", files[0])
                            element.text = "linked file: " + files[0]
                    value = "".join(root.itertext())
                except:
                    pass
                    # print "ERROR with " + value
        if col in cols:
            worksheet.write(row, cols.index(col), value)
            worksheet.set_row(row, None, None, {'level': deepth})
        if len(files) > 0:
            worksheet.insert_image(row, cols.index(col), os.path.splitext(files[0])[0] + ".png")

    for id,child in asd["children"].items():
        row = workOnHierarch(child, row=row+1, cols=cols, deepth=deepth+1, worksheet=worksheet)
    return row

def dump(myDoc, outfile, basepath = None):
    row = 0
    if basepath is None:
        basepath = os.path.dirname(outfile)
    workbook = xlsxwriter.Workbook(outfile)

    worksheet = workbook.add_worksheet("Export")

    cols = myDoc.fields
    colNr = 0
    for col in cols:
        worksheet.write(0, colNr, col)
        colNr += 1

    hierarchSpec = myDoc.asHierarchDict()
    for id, topElement in hierarchSpec[0].items():
        row = workOnHierarch(topElement, cols = myDoc.fields, row=row+1, worksheet = worksheet)
    workbook.close()
