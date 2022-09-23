from setuptools import setup

with open("scheduler/__init__.py", "r") as file:
    for line in file:
        if "__version__" in line:
            version = line.split('"')[1]
        if "__author__" in line:
            author = line.split('"')[1]

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

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
    extras_require={
        "yaml": "PyYAML=>6.0",
    },
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
