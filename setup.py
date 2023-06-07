from setuptools import find_packages, setup

with open("./README.md") as fp:
    long_description = fp.read()

setup(
    name="python-arango",
    description="Python Driver for ArangoDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Joohwan Oh",
    author_email="joohwan.oh@outlook.com",
    url="https://github.com/ArangoDB-Community/python-arango",
    keywords=["arangodb", "python", "driver"],
    packages=find_packages(exclude=["tests"]),
    package_data={"arango": ["py.typed"]},
    include_package_data=True,
    python_requires=">=3.8",
    license="MIT",
    install_requires=[
        "urllib3>=1.26.0",
        "requests",
        "requests_toolbelt",
        "PyJWT",
        "setuptools>=42",
        "importlib_metadata>=4.7.1",
        "packaging>=23.1",
    ],
    extras_require={
        "dev": [
            "black>=22.3.0",
            "flake8>=4.0.1",
            "isort>=5.10.1",
            "mypy>=0.942",
            "mock",
            "pre-commit>=2.17.0",
            "pytest>=7.1.1",
            "pytest-cov>=3.0.0",
            "sphinx",
            "sphinx_rtd_theme",
            "types-pkg_resources",
            "types-requests",
            "types-setuptools",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation :: Sphinx",
    ],
)
