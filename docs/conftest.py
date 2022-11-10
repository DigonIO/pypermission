from doctest import ELLIPSIS
from sybil import Sybil, Document
from sybil.parsers.capture import parse_captures
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.skip import skip

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
        skip,
    ],
    patterns=["pages/examples/quick_start.rst"],
    # patterns=["pages/*/*.rst"],
    fixtures=["serial_authority_typed"],
).pytest()
