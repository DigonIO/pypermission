from setuptools import setup

setup(
    name="pypermission",
    python_requires=">=3.10",
    packages=["pypermission"],
    package_dir={"": "src"},
    extras_require={
        "yaml": "PyYAML=>6.0",
    },
)
