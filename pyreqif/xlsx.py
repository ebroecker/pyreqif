#!/usr/bin/env python2
import io
import os.path
from lxml import etree
import pyreqif.extractOleData
import xlsxwriter

def write_excel_line(worksheet, item, row, cols, depth, basepath):
    files = []

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
                        files = pyreqif.extractOleData.extractOleData(rtfFilename)

                        if len(files) > 0:
                            for key in element.attrib:
                                del element.attrib[key]
                            element.tag = "a"
                            element.set("href", files[0])
                            element.text = "linked file: " + files[0]
                    value = "".join(root.itertext())
                    value = value.encode("utf8")
                except:
                    pass
        worksheet.write(row, cols.index(col), value.decode("utf-8"))
        worksheet.set_row(row, None, None, {'level': depth})
        if len(files) > 0:
            worksheet.insert_image(row, cols.index(col), os.path.splitext(files[0])[0] + ".png")


def dump(myDoc, outfile, basepath = None):
    if basepath is None:
        basepath = os.path.dirname(outfile)
    workbook = xlsxwriter.Workbook(outfile)

    worksheet = workbook.add_worksheet("Export")

    cols = myDoc.fields
    colNr = 0
    for col in cols:
        worksheet.write(0, colNr, col)
        colNr += 1
    cols = myDoc.fields
    row = 0

    for child in myDoc.hierarchy:
        for item, depth in  myDoc.hierach_iterator(child, cols):
            row += 1
            write_excel_line(worksheet, item, row, cols, depth, basepath)
    workbook.close()
