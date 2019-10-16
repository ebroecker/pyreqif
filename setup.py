"""very basic python implementation of reqif object model with import and export feature ...

        supported file formats for import:
        
            .reqif
            .rif

        
        
        supported file formats for export:
        
            .rif 
            
	    .xlsx
            
            .html
"""

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
License :: OSI Approved :: BSD License
Topic :: Scientific/Engineering
"""

import sys
from setuptools import setup, find_packages

doclines = __doc__.split("\n")

setup(
    name = "pyreqif",
    version = 0.2,
    maintainer = "Eduard Broecker",
    maintainer_email = "eduard@gmx.de",
    url = "http://github.com/ebroecker/pyreqif",
    classifiers = filter(None, classifiers.split("\n")),
    description = doclines[0],
    keywords = "reqif requirements interchange format",
    long_description = "\n".join(doclines[2:]),
    license = "BSD",
    platforms = ["any"],
    install_requires = ["future", "oletools", "lxml", "xlsxwriter"],

    packages = find_packages(),
    scripts=['reqif2html.py', 'reqif2xlsx.py']
)

