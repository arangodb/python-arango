import os
import sys

from setuptools import setup, find_packages


setup(
    name="arango",
    description="Python Driver for ArangoDB",
    version="2.3.4",
    author="Joohwan Oh",
    author_email="joowani88@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests"],
    test_suite="nose",
)