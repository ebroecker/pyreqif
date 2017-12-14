"""very basic python implementation of reqif object model with import and export feature ...

        supported file formats for import:
        
            .reqif
        
        
        supported file formats for export:
        
            .reqif
        
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
    version = 0.1,
    maintainer = "Eduard Broecker",
    maintainer_email = "eduard@gmx.de",
    url = "http://github.com/ebroecker/pyreqif",
    classifiers = filter(None, classifiers.split("\n")),
    description = doclines[0],
    keywords = "reqif requirements interchange format",
    long_description = "\n".join(doclines[2:]),
    license = "BSD",
    platforms = ["any"],
    install_requires = ["future"],
    extras_require = {
        "reqif": ["lxml"],
        "xlsx": ["xlsxwriter"],
    },

    packages = find_packages(),
    scripts=['reqif2html.py', 'reqif2xlsx.py']
)

