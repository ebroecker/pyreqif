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

