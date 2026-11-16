#!/bin/sh

python3 createReqDoc.py &&
python3 reqif2xlsx.py aa.reqif aa.xlsx && 
python3 reqif2html.py aa.reqif aa.html &&
python3 example.py aa.reqif &&
python3 xlsx2reqif.py aa.xlsx &&


# once again with the reqif created from xlsx:
python3 reqif2xlsx.py aa.reqif aa.xlsx &&
python3 reqif2html.py aa.reqif aa.html &&
python3 example.py aa.reqif 


# validate generated reqif files against the official ReqIF schema
python3 schema_check.py aa.reqif
python3 - <<'EOF'
import zipfile
with zipfile.ZipFile("aa.reqifz") as zf:
    open("aa_from_xlsx.reqif", "wb").write(zf.read("aa.reqif"))
EOF
python3 schema_check.py aa_from_xlsx.reqif
