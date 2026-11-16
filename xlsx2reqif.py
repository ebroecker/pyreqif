#!/usr/bin/env python3
import os
import re
import zipfile
import datetime
import xml.etree.ElementTree
import openpyxl
import pyreqif.create
import pyreqif.reqif
import io
import sys


def get_images_from_excel(excel_file):
    in_excel = zipfile.ZipFile(excel_file)
    if "xl/drawings/drawing1.xml" not in in_excel.namelist():
        return []
    
    out_zip = zipfile.ZipFile(document_title + ".reqifz", 'w', zipfile.ZIP_DEFLATED)

    ns = "{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}"
    a_ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

    drawing_source = in_excel.open("xl/drawings/drawing1.xml")
    drawing_tree = xml.etree.ElementTree.parse(drawing_source)
    drawing_root = drawing_tree.getroot()

    images = [{"row":int(anchor.find(ns + "from/" + ns + "row").text),
               "col": int(anchor.find(ns + "from/" + ns + "col").text),
               "img_ref": anchor.find(ns + "pic/" + ns + "blipFill/" + a_ns + "blip").attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"]}
            for anchor in drawing_root]

    drawing_source.close()
    drawing_links_source = in_excel.open("xl/drawings/_rels/drawing1.xml.rels")
    drawing_links_tree = xml.etree.ElementTree.parse(drawing_links_source)
    drawing_links_root = drawing_links_tree.getroot()

    for relation_ship in drawing_links_root:
        id = relation_ship.attrib["Id"]
        target = relation_ship.attrib["Target"]
        for item in images:
            if item["img_ref"] == id:
                item["target"] = target.replace("../", "")
                # copy all images to target:
                out_zip.writestr(target.replace("../", ""), in_excel.read(target.replace("../", "xl/")),
                                 zipfile.ZIP_DEFLATED)
    drawing_links_source.close()
    out_zip.close()
    return images


def get_images(images, row, col):
    return_pictures = []
    for image in images:
        if image["row"] == row and image["col"] == col:
            return_pictures.append(image)
    return return_pictures


file_name = sys.argv[1]

document_title, _ = os.path.splitext(os.path.basename(file_name))
# identifiers must be valid xs:ID (NCName); keep only the safe characters
column_slug = lambda col: re.sub(r"[^A-Za-z0-9_.\-]", "_", col)

images = get_images_from_excel(file_name)
wb = openpyxl.load_workbook(file_name)
ws = wb.active

columns = [ws.cell(1, col_nr).value for col_nr in range(1, ws.max_column+1)]
# ignore columns without a header cell (e.g. empty columns at the end of the sheet)
valid_columns = [col for col in columns if col not in (None, "")]
# optional: a column named "LONG-NAME" provides the SPEC-OBJECT long name instead of an attribute
long_name_column = "LONG-NAME" if "LONG-NAME" in valid_columns else None
attribute_columns = [col for col in valid_columns if col != long_name_column]

#
# detect columns with an enumeration datatype from the data validations:
# a validation with a literal value list (e.g. "A,B,C") over a data column
# turns this column into a ReqIF enumeration with a drop-down in the export
#
enum_columns = {}  # excel column number (1-based) -> list of allowed values
for dv in ws.data_validations.dataValidation:
    if dv.formula1 is None:
        continue
    formula = dv.formula1.strip()
    if not (formula.startswith('"') and formula.endswith('"') and len(formula) > 2):
        continue  # skip validations referencing other ranges
    for cell_range in dv.sqref.ranges:
        if cell_range.min_row > 2:
            continue
        for col_nr in range(cell_range.min_col, cell_range.max_col + 1):
            enum_columns.setdefault(col_nr, [])
            for value in formula[1:-1].split(","):
                value = value.strip()
                if value and value not in enum_columns[col_nr]:
                    enum_columns[col_nr].append(value)

#
# collect the enum definitions per column: all cell values must be mappable
# to an enumeration value; unknown values are added to the enumeration
#
last_change = datetime.datetime.today().isoformat("T", "seconds")
enum_info = {}  # column name -> {"valueIds": {name: id}, "multiValued": bool}
for col in attribute_columns:
    col_nr = columns.index(col) + 1
    if col_nr not in enum_columns:
        continue
    value_ids = {}
    multi_valued = False
    # start with all values from the validation list, so options that are not
    # used in any cell are preserved in the datatype
    for index, name in enumerate(enum_columns[col_nr]):
        value_ids[name] = "_enumval_{}_{}".format(column_slug(col), index)
    for row_nr in range(2, ws.max_row + 1):
        cell = ws.cell(row_nr, col_nr).value
        if cell is None or not isinstance(cell, str):
            continue
        parts = [part.strip() for part in cell.split(",")]
        if len(parts) > 1 and all(part in enum_columns[col_nr] for part in parts):
            multi_valued = True
            names = parts
        else:
            names = [cell.strip()]
        for name in names:
            if not name:
                continue
            if name not in value_ids:
                if name in enum_columns[col_nr]:
                    index = enum_columns[col_nr].index(name)
                    value_ids[name] = "_enumval_{}_{}".format(column_slug(col), index)
                else:
                    print("Warning: value {!r} in column {!r} is not in the "
                          "validation list, adding it to the enumeration".format(name, col))
                    value_ids[name] = pyreqif.create.creatUUID()
    if len(value_ids) > 0:
        enum_info[col] = {"valueIds": value_ids, "multiValued": multi_valued}

#
# detect numeric columns: columns whose cells are all int or all float
# become real INTEGER/REAL datatypes instead of xhtml text.
# The ReqIF.Text column is always kept as xhtml, like the ReqIF standard wants it.
#
numeric_columns = {}  # column name -> "integer" or "real"
for col in attribute_columns:
    if col == "ReqIF.Text" or col in enum_info:
        continue
    col_nr = columns.index(col) + 1
    are_integer = True
    are_real = True
    has_value = False
    for row_nr in range(2, ws.max_row + 1):
        cell = ws.cell(row_nr, col_nr).value
        if cell is None or (isinstance(cell, str) and cell.strip() == ""):
            continue
        has_value = True
        if isinstance(cell, bool):
            are_integer = False
            are_real = False
        elif isinstance(cell, int):
            are_real = False
        elif isinstance(cell, float):
            are_integer = False
        else:
            are_integer = False
            are_real = False
    if has_value and are_integer:
        numeric_columns[col] = "integer"
    elif has_value and are_real:
        numeric_columns[col] = "real"

document_reqif_id = "_{}ReqifId-Header".format(document_title)
spec_reqif_id = "_{}ReqifId--spec".format(document_title)
doc_type_ref = "_doc_type_ref"

#
# create doc:
#
mydoc = pyreqif.create.createDocument(document_reqif_id, title=document_title)
pyreqif.create.addDocType(doc_type_ref, mydoc)
# create primitive datatype
#
pyreqif.create.addDatatype("_datatype_ID", mydoc)

#
# create columns (with real enumeration datatypes where detected)
#
for col in attribute_columns:
    if col in enum_info:
        datatype_id = "_datatype_enum_for_" + column_slug(col)
        values = {}
        for name, value_id in enum_info[col]["valueIds"].items():
            values[value_id] = {"identifier": value_id, "lastChange": last_change, "longName": name}
        pyreqif.create.addDatatype(datatype_id, mydoc, type="enum", longName=col + "_type", values=values)
        pyreqif.create.addReqType("_some_requirement_type_id", "requirement Type",
                                  "_reqtype_for_" + column_slug(col),
                                  col, datatype_id, mydoc, type="enum",
                                  multiValued=enum_info[col]["multiValued"])
    elif col in numeric_columns:
        datatype_id = "_datatype_{}_for_{}".format(numeric_columns[col], column_slug(col))
        pyreqif.create.addDatatype(datatype_id, mydoc, type=numeric_columns[col], longName=col + "_type")
        pyreqif.create.addReqType("_some_requirement_type_id", "requirement Type",
                                  "_reqtype_for_" + column_slug(col),
                                  col, datatype_id, mydoc, type=numeric_columns[col])
    else:
        pyreqif.create.addReqType("_some_requirement_type_id", "requirement Type",
                                  "_reqtype_for_" + column_slug(col),
                                  col, "_datatype_ID", mydoc)

#
# create document hierarchy head
#
myHierarch = pyreqif.create.createHierarchHead(document_title, typeRef=doc_type_ref, id=spec_reqif_id)

#
# create child elements
#
hierarch_stack = []
last_hierarch_element = myHierarch
for row_nr in range(2, ws.max_row+1):
    xls_req = dict(zip(columns, [ws.cell(row_nr, x).value for x in range(1, ws.max_column + 1)]))
    if "reqifId" not in xls_req:
        xls_req["reqifId"] = pyreqif.create.creatUUID()
    # the optional column "LONG-NAME" provides the SPEC-OBJECT long name
    long_name = xls_req[long_name_column] if long_name_column else None
    for col in attribute_columns:
        # do images:
        pictures = get_images(images, row_nr - 1, columns.index(col))
        if type(xls_req[col]) == str:
            xls_req[col] = xls_req[col].replace(">", "&gt;")
            xls_req[col] = xls_req[col].replace("<", "&lt;")
        if len(pictures) > 0:
            for pic in pictures:
                xls_req[col] = "" if xls_req[col] is None else xls_req[col]
                xls_req[col] += "<img src={}>".format(pic["target"])
        if xls_req[col] is not None:
            if col in enum_info:
                # map the cell content to enumeration value references
                parts = [part.strip() for part in str(xls_req[col]).split(",")]
                value_ids = enum_info[col]["valueIds"]
                if all(part in value_ids for part in parts if part) and any(parts):
                    pyreqif.create.addReq(xls_req["reqifId"], "_some_requirement_type_id",
                                          None, "_reqtype_for_" + column_slug(col),
                                          mydoc, longName=long_name,
                                          contentRef=[value_ids[part] for part in parts if part])
                else:
                    print("Warning: value {!r} in column {!r} does not match the "
                          "enumeration values, skipping it".format(xls_req[col], col))
            elif col in numeric_columns:
                pyreqif.create.addReq(xls_req["reqifId"], "_some_requirement_type_id",
                                      str(xls_req[col]), "_reqtype_for_" + column_slug(col),
                                      mydoc, longName=long_name, valueType=numeric_columns[col])
            else:
                pyreqif.create.addReq(xls_req["reqifId"], "_some_requirement_type_id",
                                      "<div>" + str(xls_req[col]) + "</div>", "_reqtype_for_" + column_slug(col),
                                      mydoc, longName=long_name)

    # do hierarchy
    hierarch_element = pyreqif.create.createHierarchElement(xls_req["reqifId"])
    level = ws.row_dimensions[row_nr].outline_level + 1
    if level > len(hierarch_stack):
        hierarch_stack.append(last_hierarch_element)
    elif level < len(hierarch_stack):
        hierarch_stack = hierarch_stack[0:level]

    current_head = hierarch_stack[level - 1]
    current_head.addChild(hierarch_element)
    last_hierarch_element = hierarch_element

mydoc.hierarchy.append(myHierarch)

#
# safe reqif to string
strIO = io.StringIO()
pyreqif.reqif.dump(mydoc, strIO)

# add reqifz as zip-file
zip = zipfile.ZipFile(document_title + ".reqifz", 'a', zipfile.ZIP_DEFLATED)
zip.writestr(document_title + '.reqif', strIO.getvalue())

zip.close()
