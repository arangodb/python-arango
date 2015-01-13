import os
import sys

from setuptools import setup, find_packages


setup(
    name="py-arango",
    description="Python Driver for ArangoDB",
    version="1.0.0",
    author="Joohwan Oh",
    author_email="joowani88@gmail.com",
    url="https://github.com/Joowani/py-arango",
    download_url="https://github.com/Joowani/py-arango/tarball/1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests"],
    test_suite="nose",
)