#!/usr/bin/env python2
import io
import os.path
from lxml import etree
import pyreqif.extractOleData
#import openpyxl
#from openpyxl.drawing.image import Image
import xlsxwriter
from PIL import Image
import urllib

def write_excel_line(worksheet, item, row, cols, depth, basepath, format):
    row_height = 0

    for col, value in item.items():
        col_height = 0
        files = []
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
                        try:
                            rtfFilename = urllib.parse.unquote(rtfFilename)
                        except:
                            pass
                        if rtfFilename.endswith(".ole"):
                            files += pyreqif.extractOleData.extractOleData(rtfFilename)
                        else:
                            files += [rtfFilename]
                        if len(files) > 0 and files[0][-3:].lower() not in ["png","jpeg","jpg","bmp","wmf","emf"]:
                            for key in element.attrib:
                                del element.attrib[key]
                            element.tag = "a"
                            element.set("href", files[0])
                            element.text = "linked file: " + files[0]
                    value = "".join(root.itertext())
                    value = value.encode("utf8")
                except:
                    pass
#        worksheet.cell(row=row, column=cols.index(col)+1). value=value.decode("utf-8")
#        worksheet.row_dimensions[row].outlineLevel = depth
        worksheet.write(row, cols.index(col), value.decode("utf-8"))
        for file in files:
            if file[-3:].lower() in ["png", "jpeg", "jpg", "bmp", "wmf", "emf"]:
                try:
                    im = Image.open(file)
                    _, height = im.size
                    col_height += height
                    im.close()
                except:
                    print("Error with image: {}".format(file))
                    col_height = max(300, row_height)

            if file[-3:].lower() in ["png", "jpeg", "jpg", "bmp", "wmf", "emf"]:
                worksheet.insert_image(row, cols.index(col), file, {'y_offset' : col_height-height})
        row_height = max(row_height, col_height)
    if row_height == 0:
        worksheet.set_row(row, None, format, {'level': depth})
    else:
        worksheet.set_row(row, row_height, None, {'level': depth})


def dump(myDoc, outfile, basepath = None):
    if basepath is None:
        basepath = os.path.dirname(outfile)
    #workbook = openpyxl.Workbook()
    #worksheet = workbook.active
    #workbook.title = "Export"
    workbook = xlsxwriter.Workbook(outfile)
    worksheet = workbook.add_worksheet("Export")

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    cols = myDoc.fields + ["reqifId"]
    colNr = 0
#    colNr = 1
    for col in cols:
        worksheet.write(0, colNr, col)
#        worksheet.cell(row=1, column=colNr).value = col
        colNr += 1
    worksheet.set_column(0, colNr, 20)
    if "ReqIF.Text" in cols:
        worksheet.set_column(cols.index("ReqIF.Text"), cols.index("ReqIF.Text"), 100)
    row = 0
#    row = 1

    for child in myDoc.hierarchy:
        for item, depth in myDoc.hierach_iterator(child, cols):
            row += 1
            write_excel_line(worksheet, item, row, cols, depth, basepath, cell_format)
#    workbook.save(filename=outfile)
    workbook.close()
