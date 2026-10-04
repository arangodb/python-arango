# Quickstart

python-arango is a Python driver for ArangoDB. Run the commands below from the
repository root.

## Repository layout

- `arango/`: driver implementation, public APIs, and type annotations.
- `tests/`: pytest tests; `conftest.py` defines database fixtures and CLI options.
- `tests/static/`: server configurations and test data used by `starter.sh`.
- `docs/`: Sphinx documentation in reStructuredText.
- `pyproject.toml`, `setup.cfg`, `.pre-commit-config.yaml`: packaging and tooling.
- `.circleci/`, `.github/workflows/`: CI checks, documentation, and publishing.

## Development setup

Use Python 3.10 or newer. Create a virtual environment, or use an existing one:

```bash
python3 -m venv .venv               # Create an isolated Python environment.
source .venv/bin/activate           # Use its interpreter and tools.
python -m pip install -e '.[dev]'   # Install the editable driver and dev tools.
pre-commit install                  # Enable checks before each commit.
```

Examples use `python` from the activated environment. If it is unavailable on
PATH, invoke your environment's interpreter directly.

## Local cluster and tests

The starter requires Docker, Bash, `wget`, and `jq`. To replace an existing test
container, run `docker stop arango` and `docker rm arango` first.

```bash
version="latest"  # Or pin a supported version, such as 3.12.10.
./starter.sh cluster enterprise "$version"  # Start a local test cluster.
python -m pytest --cluster  # Run the full suite against the cluster.
# Run one test while developing a document change.
python -m pytest --cluster tests/test_document.py::test_document_insert
# Generate an HTML coverage report.
python -m pytest --cluster --cov=arango --cov-report=html
```

Defaults are `127.0.0.1:8529`, user `root`, password `passwd`, and JWT secret
`secret`, matching the starter configuration. Override them with `--host`,
`--port`, `--root`, `--password`, and `--secret`. Use a disposable development
database: tests create and delete databases, users, jobs, and backups. If a
sandbox blocks localhost access, rerun with the required sandbox permission.

For a single server, use `./starter.sh single enterprise "$version"` and omit
`--cluster`. Import tests can run without ArangoDB:

```bash
python -m pytest tests/test_imports.py --skip-arango-setup  # Check imports offline.
```

## Style and documentation

Run the configured hooks for formatting, import ordering, linting, and type
checks. Build and test documentation separately:

```bash
pre-commit run --all-files  # Run hooks; formatters may modify files.
python -m sphinx -b html docs docs/_build  # Build the HTML documentation.
python -m sphinx -b doctest docs docs/_build  # Test documentation examples.
```

The Sphinx doctests require a running ArangoDB server. Open
`docs/_build/index.html` for the HTML documentation or `htmlcov/index.html` for
the coverage report.

## Changes and pull requests

- Agents must work on a branch other than `main`; never commit directly to `main`.
  Check the current branch before editing or committing. If on `main` or a
  detached HEAD, create a branch first:

  ```bash
  git branch --show-current  # Check the current branch.
  git switch -c fix/describe-change  # Choose a descriptive branch name.
  ```

- Preserve public API compatibility unless a breaking change is intentional.
- Follow existing code patterns, type annotations, and Sphinx docstrings.
- Add regression tests for fixes and tests for new behavior; update user documentation.
- Run relevant tests and checks; report anything skipped and why.
- Keep test coverage at 100% and squash changes into one commit for submission,
  as described in `docs/contributing.rst`.
- Use present-tense commit messages, such as `Fix cursor retry`.
- Explain what changed, why, and any compatibility impact in the pull request.
