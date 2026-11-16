#!/usr/bin/env python3
"""validate generated reqif files against schema/reqif.xsd"""
import sys
import xmlschema

schema = xmlschema.XMLSchema("schema/reqif.xsd")

failed = False
for file in sys.argv[1:]:
    errors = list(schema.iter_errors(file))
    if errors:
        failed = True
        print("{}: INVALID".format(file))
        for error in errors[:10]:
            print("  -", str(error).split("\n")[0])
    else:
        print("{}: valid".format(file))

raise SystemExit(1 if failed else 0)
