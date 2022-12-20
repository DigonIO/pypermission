from enum import Enum

from setuptools import setup

with open("src/pypermission/__init__.py", "r") as file:
    content = file.read()
    co = compile(content, "header.py", "exec")
    version = co.co_consts[co.co_names.index("__version__")]
    author = co.co_consts[co.co_names.index("__author__")]

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


class Dependecy(str, Enum):
    PYYAML = "PyYAML>=6.0"
    SQLALCHEMY = "sqlalchemy==1.4.42"
    NUMPYDOC = "numpydoc==1.5.0"
    SPHINX = "Sphinx==5.2.3"
    SPHINX_MERMAID = "sphinxcontrib-mermaid==0.7.1"
    M2R2 = "m2r2==0.3.3"
    DOCUTILS = "docutils==0.19"
    FURO = "furo==2022.9.29"
    PYTEST = "pytest==7.1.3"
    PYTEST_COV = "pytest-cov==4.0.0"
    COVERAGE = "coverage==6.5.0"
    DEEPDIFF = "deepdiff==6.2.1"
    SYBIL = "sybil==3.0.1"
    MYPY = "mypy==0.981"
    BANDIT = "bandit==1.7.4"
    PYLINT = "pylint==2.14.5"
    PYDOCSTYLE = "pydocstyle==6.1.1"
    TYPES_PYYAML = "types-PyYAML>=6.0.12"
    MARIADB = "mariadb>=1.1.5.post2"
    TYPING_EXTENSIONS = "typing-extensions==4.4.0"
    MYPY_EXTENSIONS = "mypy-extensions==0.4.3"
    SQLALCHEMY2_STUBS = "sqlalchemy2-stubs==0.0.2a29"
    PRE_COMMIT = "pre-commit==2.20.0"
    SCHEDULER = "scheduler==0.8.0"
    BLACK = "black==22.10.0"
    BLACKEN_DOCS = "blacken-docs==1.12.1"
    ISORT = "isort==5.10.1"
    SETUPTOOLS = "setuptools==65.6.3"  # weird bug with m2r2 otherwise


Dep = Dependecy

REQ_YAML = {Dep.PYYAML}
REQ_SQLALCHEMY = {Dep.SQLALCHEMY}
REQ_ALL = REQ_YAML | REQ_SQLALCHEMY

REQ_LINT = REQ_ALL | {
    Dep.MYPY,
    Dep.BANDIT,
    Dep.PYLINT,
    Dep.PYDOCSTYLE,
    Dep.NUMPYDOC,
    Dep.TYPES_PYYAML,
    Dep.TYPING_EXTENSIONS,
    Dep.MYPY_EXTENSIONS,
    Dep.SQLALCHEMY2_STUBS,
}
REQ_DOC = REQ_ALL | {
    Dep.SPHINX,
    Dep.M2R2,
    Dep.DOCUTILS,
    Dep.FURO,
    Dep.NUMPYDOC,
    Dep.TYPING_EXTENSIONS,
    Dep.SPHINX_MERMAID,
    Dep.SETUPTOOLS,
}
REQ_TEST = REQ_LINT | {
    Dep.PYTEST,
    Dep.PYTEST_COV,
    Dep.COVERAGE,
    Dep.DEEPDIFF,
    Dep.SYBIL,
    Dep.SCHEDULER,
    Dep.MARIADB,
}
REQ_DEV = REQ_DOC | REQ_TEST | {Dep.PRE_COMMIT, Dep.BLACK, Dep.BLACKEN_DOCS, Dep.ISORT}

req_to_str_list = lambda req: [entry.value for entry in req]

EXTRAS_REQUIRE = {
    "yaml": req_to_str_list(REQ_YAML),
    "sqlalchemy": req_to_str_list(REQ_SQLALCHEMY),
    "all": req_to_str_list(REQ_ALL),
    "lint": req_to_str_list(REQ_LINT),
    "doc": req_to_str_list(REQ_DOC),
    "test": req_to_str_list(REQ_TEST),
    "dev": req_to_str_list(REQ_DEV),
}

setup(
    name="PyPermission",
    version=version,
    author=author,
    author_email="devops@digon.io",
    license="LGPLv3",
    description="A node based permission engine for python.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords="permission engine system node tree",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.10",
    extras_require=EXTRAS_REQUIRE,
    packages=[
        "pypermission",
        "pypermission.serial",
        "pypermission.sqlalchemy",
    ],
    package_dir={"": "src"},
    package_data={"pypermission": ["py.typed"]},
    url="https://gitlab.com/DigonIO/PyPermission",
    project_urls={
        "Documentation": "https://PyPermission.readthedocs.io/en/latest/",
        "Source Code": "https://gitlab.com/DigonIO/PyPermission",
        "Bug Tracker": "https://gitlab.com/DigonIO/PyPermission/-/issues",
        "Changelog": "https://gitlab.com/DigonIO/PyPermission/-/blob/master/CHANGELOG.md",
    },
)
