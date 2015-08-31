from setuptools import setup, find_packages


setup(
    name="python-arango",
    description="Python Driver for ArangoDB",
    version="2.1.0",
    author="Joohwan Oh",
    author_email="joohwan.oh@outlook.com",
    url="https://github.com/Joowani/python-arango",
    download_url="https://github.com/Joowani/python-arango/tarball/2.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests"],
    test_suite="nose",
)
