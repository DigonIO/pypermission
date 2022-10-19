from setuptools import setup

with open("src/pypermission/__init__.py", "r") as file:
    for line in file:
        if "__version__" in line:
            version = line.split('"')[1]
        if "__author__" in line:
            author = line.split('"')[1]

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

DEP_NUMPY_DOC = [
    "numpydoc==1.5.0",
]

REQUIRE_YAML = [
    "PyYAML>=6.0",
]


REQUIRE_DOC = [
    "Sphinx==5.2.3",
    "m2r2==0.3.3",
    "docutils==0.19",
    "furo==2022.9.29",
] + DEP_NUMPY_DOC

REQUIRE_TEST = [
    "pytest==7.1.3",
    "pytest-cov==4.0.0",
    "coverage==6.5.0",
    "deepdiff==6.2.1",
]

REQUIRE_LINT = [
    "mypy==0.981",
    "bandit==1.7.4",
    "pylint==2.14.5",
    "pydocstyle==6.1.1",
    # below typing stubs
    "types-PyYAML>=6.0.12",
] + DEP_NUMPY_DOC

EXTRAS_REQUIRE = {
    "yaml": REQUIRE_YAML,
    "doc": REQUIRE_YAML + REQUIRE_DOC,
    "dev": REQUIRE_YAML + REQUIRE_DOC + REQUIRE_TEST + REQUIRE_LINT,
    "test": REQUIRE_YAML + REQUIRE_TEST,
    "lint": REQUIRE_YAML + REQUIRE_LINT,
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
    packages=["pypermission"],
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
