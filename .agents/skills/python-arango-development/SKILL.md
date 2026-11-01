---
name: python-arango-development
description: >-
  Maintain and extend python-arango, the ArangoDB Python driver. Use for
  driver features, bug fixes, refactoring, and related tests or documentation,
  rather than application code that uses the driver.
---

# Python driver development

Follow the repository's [AGENTS.md](../../../AGENTS.md) for setup, validation
commands, and contribution rules.

Before changing an operation, trace a neighboring method with a similar
request and response shape. Public API methods usually construct a `Request`,
define a response handler, and call `self._execute(request, response_handler)`.
See `arango/api.py`, `arango/request.py`, and the API group being changed.
Keep request construction and response conversion at the same layer as the
neighboring operations.

Preserve execution through `_execute` when following this pattern. It delegates
to the configured executor in `arango/executor.py`, supporting default, async,
batch, and transaction contexts. Calling the connection directly can bypass
that behavior. Preserve `Result[T]` annotations where applicable: an operation
can return a value, an async or batch job, or `None`, depending on its context.
See `arango/result.py` for the shared type.

For endpoint or option changes, verify the server HTTP API for the targeted
ArangoDB versions. Map Python option names to the specified wire names and
locations: endpoint path, `params` for query parameters, `headers`, or `data`
for the body. Preserve existing defaults and distinguish omitted options from
explicit `False`, `0`, or empty values. Where `None` means omission, use
`is not None` rather than a truthiness check. `normalize_params` in `arango/request.py`
stringifies supplied values, including `None`; omit such query entries before
constructing the request. Keep explicit JSON nulls where the body contract
requires them.

Follow the neighboring handler's success checks and response formatting;
reuse helpers in `arango/formatter.py` where applicable. Preserve Python-facing
field names, return shapes, and silent-operation results. Handle special
statuses before the general failure check where required, such as revision
conflicts. Raise the operation-specific exception from `arango/exceptions.py`
with `(resp, request)` to retain HTTP and ArangoDB error details. Keep signatures,
annotations, and Sphinx parameter and return documentation aligned. Cover
omitted and explicit option values, result conversion, and affected error
paths in regression tests.

Add focused regression coverage in the relevant `tests/test_*.py` module,
reusing fixtures and helpers from `tests/conftest.py` and `tests/helpers.py`.
Check the affected request mapping, result, or error behavior; exercise related
execution contexts when the change affects them.

For test selection, inspect fixture dependencies in `tests/conftest.py`.
Pytest normally connects to ArangoDB and creates test resources during
configuration, even for database-free tests or collection. Use
`--skip-arango-setup` only for tests that need no configured database fixtures,
for example:

```sh
python -m pytest tests/test_request.py --skip-arango-setup
```

This flag bypasses setup; it does not make integration tests run offline.
For server behavior, run the relevant test against a disposable ArangoDB
instance using AGENTS.md. Match the actual topology: pass `--cluster` for a
cluster, omit it for a single server. The flag does not start a cluster.
Check version and capability skips in the selected tests; skipped cases do
not validate the change. Start with the affected test, expand for changed
contracts, and report any unverified behavior.
