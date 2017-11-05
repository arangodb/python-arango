.. _contributing-page:

Contributing
------------

Instructions
============

Before you submit a pull request on GitHub_, please make sure you meet the
following requirements:

* All changes are squashed into a single commit (I use git rebase -i).
* Commit message in present tense (yes: "Add feature" no: "Added feature").
* Correct and consistent style (e.g. Sphinx_-compatible docstrings, PEP8).
* No missing docstrings or commented-out lines.
* The test coverage_ remains at %100.
* No build failures on TravisCI_.
* Does not break backward-compatibility (unless you have a good reason to).
* Must be compatible with all Python versions supported.


Style
=====

To ensure that your changes have no PEP8 errors, please run flake8_:

.. code-block:: bash

    ~$ pip install flake8
    ~$ git clone https://github.com/joowani/python-arango.git
    ~$ cd python-arango
    ~$ flake8

You *must* resolve all issues reported from the check.

Testing
=======

To test your changes, you can run the integration test suite that comes with
**python-arango** on your local machine. The test suite uses pytest_, and runs
against an actual database instance. Please use the latest version of ArangoDB
with default configuration:

* **Host**: "localhost"
* **Port**: 8529
* **Username**: "root"
* **Password**: ""

To run the test suite:

.. code-block:: bash

    ~$ pip install pytest
    ~$ git clone https://github.com/joowani/python-arango.git
    ~$ cd python-arango
    ~$ py.test --verbose

To run the test suite with coverage report:

.. code-block:: bash

    ~$ pip install coverage pytest pytest-cov
    ~$ git clone https://github.com/joowani/python-arango.git
    ~$ cd python-arango
    ~$ py.test --verbose --cov-report=html --cov=arango
    ~$ # Open the generated file htmlcov/index.html in your browser

The test suite only operates on temporary databases created during the run.
Regardless, you should only run it against test ArangoDB instances.

Documentation
=============

The documentation (including the README) is written in reStructuredText and
uses Sphinx_. To build the HTML version of the documentation on your local
machine:

.. code-block:: bash

    ~$ pip install sphinx sphinx_rtd_theme
    ~$ git clone https://github.com/joowani/python-arango.git
    ~$ cd python-arango/docs
    ~$ sphinx-build . build
    ~$ # Open the generated file build/index.html in your browser


As always, thank you for your contribution!

.. _GitHub: https://github.com/joowani/python-arango
.. _coverage: https://coveralls.io/github/joowani/python-arango
.. _TravisCI: https://travis-ci.org/joowani/python-arango
.. _Sphinx: https://github.com/sphinx-doc/sphinx
.. _flake8: http://flake8.pycqa.org
.. _pytest: https://github.com/pytest-dev/pytest

