#!/usr/bin/env python2

import pyreqif.pyreqif
import pyreqif.reqif
import xlsxwriter
import io
from lxml import etree


myDoc = pyreqif.reqif.load("aa.xml")
#f = open("bb.xml", "w")
#pyreqif.reqif.dump(myDoc, f)

workbook = xlsxwriter.Workbook("test.xlsx")

for specification in myDoc.specificationList:
    worksheet = workbook.add_worksheet(specification.name)
    row = 0
    cols = []
    for req in specification:
        reqObj = myDoc.getReqById(req)
        for col in myDoc.flatReq(reqObj, html=True):
            if col  not in cols:
                cols.append(col)

    colNr = 0
    for col in cols:
        worksheet.write(0, colNr, col)
        colNr += 1
        
    for req in specification:
        row += 1
        reqObj = myDoc.getReqById(req)
        for col,value in myDoc.flatReq(reqObj, html=True).iteritems():
            worksheet.write(row,cols.index(col),value)
            if value is not None:
                if "<" in value:
                    try:
                        tree = etree.parse(io.BytesIO(value))
                        root = tree.getroot()
                        for element in root.iter("object"):
                            print value
                            print element.attrib["name"]
                            print element.attrib["data"]
                            print element.attrib["type"]
                            root.remove(element)
                            value = etree.tostring(root)
                            print value
                            print "\n\n"

                    except:
                        pass
#                print value
#                print "\n\n"
                pass
#
#                 print value
workbook.close()

##req = myDoc.getReqById("_640aba33-6f1e-49b3-bbf5-df798a7786bd")
##req = myDoc.getReqById("_e747a0ca-ea6f-4b8a-b20d-893759701799")
##pprint(vars(req), indent=2)
##print myDoc.flatReq(req)


#def printHierarch(asd, deepth=0):
#        print deepth,
#        print asd._identifier
#        for child in asd._children:
#            printHierarch(child, deepth+1)

#for req in myDoc._hierarchy:    
#    printHierarch(req)    
