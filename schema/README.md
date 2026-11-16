# ReqIF schema files

`reqif.xsd` (namespace `http://www.omg.org/spec/ReqIF/20110401/reqif.xsd`) and
`driver.xsd` are taken from the OMG ReqIF 1.0 formal specification
(https://www.omg.org/spec/ReqIF/). OMG permits distribution of its
specification material; these files are included here unmodified apart from
 locally resolvable includes.

`xml.xsd` and the `xhtml-*.xsd` modules are the XHTML 1.1 modular schemas
from the W3C (https://www.w3.org/MarkUp/SCHEMA/ and https://www.w3.org/2001/).
They are redistributed under the W3C Software and Document license
(https://www.w3.org/copyright/software-license-2023/):

> Copyright © 1994-2025 World Wide Web Consortium.
> (Massachusetts Institute of Technology, European Research Consortium for
> Informatics and Mathematics, Keio University, Beihang). All Rights Reserved.
> This work is distributed under the W3C® Software and Document License;
> see the license text at the URL above.

Modification note: the `schemaLocation` attributes in these files were
rewritten from absolute W3C URLs to relative file names so that the whole
include chain resolves locally (this is what makes offline schema validation
possible).

Validation entry point: `python3 schema_check.py <file.reqif>...` from the
repository root.
