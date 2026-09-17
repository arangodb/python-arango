# Painpoints to address with the next major release

## JWT authentication

The driver supports JWTs, but renewal is reactive, unsynchronized, and can fail for expired tokens. Application-managed
tokens can incorrectly enter credential-based refresh. Reliable renewal needs clearer authentication ownership, while
changing the Basic authentication default requires a migration path.

a. Define disabled, driver-managed, and application-managed authentication modes. Make JWT the default, allow an initial
   JWT alongside credentials in driver-managed mode, and document migration.

b. Add proactive renewal with bounded retries and one acquisition shared by concurrent requests. Define renewal worker
   ownership and cleanup.

c. Fix expired-token recovery and retry rejected requests once. Reuse newer tokens after delayed 401s, and never refresh
   application-managed tokens using credentials.

d. Test expiration, concurrent renewal, failed acquisition, and application-managed replacement. Correct the expiry test
   to update both the token and its recorded expiration.

e. Add `db.update_jwt(token)` for application-managed tokens, delegating to the connection's token replacement. Scope
   updates to that authentication context, not the entire ArangoClient: separate database connections can use different
   credentials. Make replacement safe during concurrent requests, without recreating connections or triggering renewal.
   Subsequent requests through the database and its existing collection wrappers must use the replacement token;
   requests already in progress may finish with the previous token. Other authentication contexts remain unaffected.

f. Keep renewal state per authentication context. Track contexts created by the client so `client.close()` stops all
   associated renewal activity, including preventing in-progress renewals from scheduling new tasks after shutdown.

`alice_db.update_jwt(new_alice_token)` is a proposed public API; the current equivalent is
`alice_db.conn.set_token(new_alice_token)`. A separate `bob_db` connection remains unaffected, even when both were
created through the same client. The specification's "root instance" should therefore mean the authentication context
for this operation, rather than requiring a single client-wide token.

## Concurrency

Using the driver across threads lacks clear guarantees around shared sessions, mutable connection state, and JWT
renewal. Both a shared ArangoClient and separate clients per thread should support parallel requests. Stateful cursors
also need explicit ownership rules to prevent overlapping fetches and inconsistent iteration.

a. Support both client usage patterns and document which database and collection wrappers can be shared. Define session
   ownership without serializing all requests.

b. Make pool sizing and acquisition timeouts predictable. Verify and fix the suspected pool_timeout wiring issue, then
   test pool exhaustion.

c. Synchronize shared resolver and JWT state, and define shutdown behavior during active requests. Keep separate clients
   independent.

d. Support independent cursors for concurrent queries. Document each cursor as having one consumer, including iteration,
   fetching, batch access, and closing.

e. Test both client usage patterns with overlapping requests, independent cursors, JWT renewal, and shutdown. Check for
   deadlocks and blocked threads after failures.

## API versioning

Versioned APIs can change accepted parameters, response fields, and endpoint behavior. Supporting them requires more
than changing URL prefixes: the driver must preserve existing Python calls while exposing incompatible contracts through
clear method signatures and accurate type hints.

a. Add optional API version selection to client.db(), retaining legacy behavior when omitted. Keep the selected policy
   fixed on the connection and propagate it through cursors and execution contexts.

b. Group operation-specific request builders and response decoders into adapters selected by each version policy. Reuse
   unchanged adapters and keep authentication, transport, and retries separate.

c. Preserve StandardCollection as the legacy interface. Share unchanged methods through a common base and introduce
   sibling version-specific wrappers where signatures or result contracts differ.

d. Use Literal overloads to select typed database and collection wrappers, and TypedDict definitions for
   version-specific results. Preserve missing legacy fields only when they can be derived accurately.

e. Validate version support and reject unsupported operations explicitly. Test legacy compatibility, version-specific
   requests and results, type inference, and version propagation across execution contexts.

### Examples

These sketches describe proposed interfaces, not current driver features. The index parameters and result fields are
hypothetical; omitted implementations use `...`.

Existing calls retain their behavior, while callers explicitly opt into a new contract:

```python
legacy = client.db("example", **credentials)
modern = client.db("example", api_version="v1", **credentials)

legacy.collection("docs").index(foo="bar")
result = modern.collection("docs").index(foo={"bar": "bar"})
```

Each policy groups adapters for its contract. Adapters build complete requests and decode successful responses;
existing response handlers retain operation-specific exceptions and use `_execute()` to preserve execution contexts.

```python
legacy_policy = ApiPolicy(
    indexes=LegacyIndexAdapter(),
    aql=LegacyAqlAdapter(),
    cursors=LegacyCursorAdapter(),
)
v1_policy = ApiPolicy(
    indexes=V1IndexAdapter(),
    aql=V1AqlAdapter(),
    cursors=V1CursorAdapter(),
)

class V1IndexAdapter:
    def build_create_request(self, collection, definition) -> Request:
        ...

    def decode_create_response(self, body) -> dict:
        ...
```

Unchanged public methods share a base implementation. Incompatible methods belong to sibling classes, with separate
parameter and result types. Here, StandardCollection retains the legacy role discussed as V0Collection.

```python
from typing import TypedDict

from arango.api import ApiGroup
from arango.result import Result


class V1IndexOptions(TypedDict):
    bar: str


class V0IndexResult(TypedDict):
    id: str
    legacy_field: str


class V1IndexResult(TypedDict):
    id: str


class CommonCollection(ApiGroup):
    def count(self) -> Result[int]:
        ...


class StandardCollection(CommonCollection):
    def index(self, *, foo: str) -> Result[V0IndexResult]:
        ...


class V1Collection(CommonCollection):
    def index(self, *, foo: V1IndexOptions) -> Result[V1IndexResult]:
        ...
```

Both collection classes inherit `count()`. Their `index()` implementations delegate to version-specific adapters;
V1Collection does not override StandardCollection with an incompatible signature. V1IndexResult has no legacy_field.

Overloads connect version selection to the returned wrapper type. This sketch abbreviates existing arguments;
the actual signatures must preserve them and append `api_version` as a keyword-only parameter.

```python
from typing import Literal, overload


class ArangoClient:
    @overload
    def db(self, name: str, *, api_version: None = None) -> StandardDatabase: ...

    @overload
    def db(self, name: str, *, api_version: Literal["v1"]) -> V1Database: ...

    def db(self, name: str, *, api_version: str | None = None):
        ...
```

StandardDatabase.collection() returns StandardCollection; V1Database.collection() returns V1Collection.
This lets type checkers reject a string passed to the v1 index method without widening both signatures to a union.

## Types

Generic dictionaries and long parameter lists make driver APIs difficult to discover and check statically. Typed inputs,
results, and query configuration objects should provide clearer signatures and property access while preserving existing
dictionary operations, JSON serialization, and method calls.

a. Add dictionary-based input and result models with typed constructors and explicit properties. Keep dictionary storage
   authoritative, preserve existing keys, and retain unknown fields where current behavior does.

b. Accept typed index definitions alongside existing dictionaries. Return models such as Result[ServerVersion], wrapping
   existing formatted responses and preserving asynchronous and batch execution behavior.

c. Add a Query object accepted by AQL.execute() alongside the full existing signature. Normalize both forms through one
   execution path without mutating reusable query configuration.

d. Describe both execute() forms with overloads and one runtime implementation. Capture extra arguments to reject mixed
   configuration, preserving existing defaults and positional arguments for string calls.

e. Test dictionary operations, properties, JSON serialization, custom serializers, and both query forms. Document
   mutation limits and use opt-in typed responses where exact dictionary types must remain compatible.

### Examples

These are proposed interfaces and abbreviated implementation sketches. Models are instances passed to methods, not
classes. The earlier TypedDict examples describe schemas; dictionary subclasses additionally provide runtime accessors.

Typed index definitions supplement existing dictionary inputs. Request definitions and returned index descriptions
should use separate models because their required fields differ.

```python
collection.add_index(VectorIndex(fields=["embedding"], params=vector_params))
collection.add_index(InvertedIndex(fields=["title"]))
collection.add_index({"type": "inverted", "fields": ["title"]})
```

A response model keeps property and dictionary access consistent, without storing a second copy of each value:

```python
import json
from typing import Any, cast


class ServerVersion(dict[str, Any]):
    @property
    def version(self) -> str:
        return cast(str, self["version"])

    @version.setter
    def version(self, value: str) -> None:
        self["version"] = value


result = ServerVersion(version="3.12.11", server="arango")
assert result.version == result["version"]
result.version = "3.12.12"
assert result["version"] == "3.12.12"
plain = dict(result)
encoded = json.dumps(result)
```

server_version() would return Result[ServerVersion], wrapping format_body(resp.body) in ServerVersion on success.
Keep existing formatting before wrapping; version adapters select different models when needed.

dict(result) makes a shallow copy. Nested values must also be JSON-compatible; a recursive to_dict() can provide plain
nested dictionaries if required. Unknown keys remain accessible through dictionary syntax.

Dictionary subclasses pass isinstance(result, dict), but not type(result) is dict. Custom serializers need compatibility
checks. Explicit properties avoid collisions with dictionary methods such as items() and keys().

cast() provides a static hint, not runtime validation. Direct dictionary mutation can still introduce invalid values or
remove required fields. Validate typed constructors or provide explicit validation without restricting legacy dictionary
operations; optional accessors should not insert absent fields into the response.

A Query object groups the text, bind variables, and execution options without replacing the existing call form:

```python
text = "FOR doc IN documents FILTER doc.active == @active RETURN doc"

cursor = db.aql.execute(text, bind_vars={"active": True}, batch_size=100)

query = Query(text=text, bind_vars={"active": True}, batch_size=100)
cursor = db.aql.execute(query=query)
```

Overloads describe the accepted forms to type checkers. One implementation dispatches on the query type; two ordinary
execute() definitions would replace one another. This sketch shows only count and batch_size; retain all existing
parameters in the actual string overload and the helper handling legacy calls.

```python
from typing import overload


class AQL:
    @overload
    def execute(self, query: Query) -> Result[Cursor]: ...

    @overload
    def execute(
        self, query: str, count: bool = False, batch_size: int | None = None
    ) -> Result[Cursor]: ...

    def execute(self, query: str | Query, *args, **kwargs) -> Result[Cursor]:
        if isinstance(query, Query):
            if args or kwargs:
                raise TypeError("A Query object cannot be combined with other arguments")
            return self._execute_query(query)
        return self._execute_legacy(query, *args, **kwargs)
```

The _execute_legacy() helper retains the full existing signature and defaults, then normalizes its arguments into the
same execution path as _execute_query(). Capturing arguments before defaults are applied distinguishes every explicit
extra argument, including None and False, without sentinels.

```python
db.aql.execute(query)                   # Accepted.
db.aql.execute(query=query)             # Accepted.
db.aql.execute(query, batch_size=None)  # TypeError: explicit extra keyword argument.
db.aql.execute(query, False)            # TypeError: explicit extra positional argument.
```

The existing Sphinx autodoc configuration rendered both overloads, including their defaults and type hints, in a
temporary build with Sphinx 8.2.3. No additional extension or configuration was needed. Keep overloads complete for IDEs
and generated API documentation; documentation dependencies currently do not pin Sphinx.

Runtime inspect.signature() still exposes (self, query, *args, **kwargs). Overloads improve static tooling and this
project's generated documentation, but do not change runtime argument binding or enforce the mixed-argument rule.

The shared execution path must preserve more than the JSON body: allow_dirty_read controls a request header, while
allow_retry also configures the returned cursor. Keep cursor state separate and snapshot mutable query configuration
as needed so executing a Query does not change it.

## Response format

Response formatting inconsistently renames keys, drops unknown fields, and changes values such as index identifiers.
Disabling formatting does not reliably preserve server data. Responses need predictable dictionary representations and
stable snake_case properties, with a compatibility mode for applications relying on historical transformations.

a. Add fixed server and legacy response formats per database wrapper, independently of API version. Make server the
   next major release's default and retain legacy indefinitely.

b. Preserve server resource keys, values, and unknown fields in server mode. Isolate historical transformations in
   legacy adapters; define unchanged server names for new fields without historical mappings.

c. Implement response models as dict subclasses with explicit snake_case properties. Store only the selected
   representation, and use sibling legacy implementations where property mappings differ.

d. Separate envelope extraction from resource formatting. Avoid mutating input dictionaries or renaming user data;
   document copying, optional properties, and value differences between representations.

e. Audit formatter.py and inline cursor transformations. Test both formats, property synchronization, serialization, and
   execution contexts; document migration, existing formatter options, and exact-dict compatibility limits.

### Examples

These are proposed interfaces. Select the format once; collections, cursors, and asynchronous or batch results inherit
that selection. API version and response format remain independent choices.

```python
modern = client.db("example", response_format="server", **credentials)
legacy = client.db("example", response_format="legacy", **credentials)
```

Both representations offer the same snake_case property names. Dictionary access and JSON serialization use the selected
keys, without storing duplicate aliases. This simplified model illustrates a required field of a TTL index:

```python
import json
from typing import Any, ClassVar, cast


class IndexInfo(dict[str, Any]):
    _expiry_key: ClassVar[str] = "expireAfter"

    @property
    def expire_after(self) -> int:
        return cast(int, self[self._expiry_key])

    @expire_after.setter
    def expire_after(self, value: int) -> None:
        self[self._expiry_key] = value


class LegacyIndexInfo(IndexInfo):
    _expiry_key = "expiry_time"


server = IndexInfo({"expireAfter": 60})
legacy = LegacyIndexInfo({"expiry_time": 60})
assert server.expire_after == legacy.expire_after

legacy.expire_after = 120
assert legacy["expiry_time"] == 120
assert dict(server) == {"expireAfter": 60}
assert json.loads(json.dumps(legacy)) == {"expiry_time": 120}
```

The response adapter prepares the selected representation and constructs its model. Actual models must reflect the
field's numeric range and optionality. Properties read dictionary storage directly, including changes made through
update() or item assignment; unrestricted dictionary mutation still cannot guarantee valid field types.

Keep legacy value and structure conversions explicit: shortening an index ID is not a key alias. Document whether
properties expose the selected stored value or a separately derived value. Do not reconstruct lost information from
legacy data or retain a second mutable dictionary that can drift out of sync.

Use the async driver's JsonWrapper properties as a reference, but inherit standard dictionary behavior instead of
reimplementing it. Its current wrapper lacks several dictionary methods, cannot be serialized directly by json.dumps(),
mutates constructor input, and exposes internal storage through to_dict().

Copy input mappings during construction. dict(model) and a basic to_dict() should return shallow copies; document nested
sharing or provide explicit recursive conversion. Envelope removal belongs in endpoint response handling, not the model
base class. Never apply generic recursive key conversion to documents, bind variables, or user-defined names.

Retaining legacy indefinitely requires permanent compatibility tests. Freeze historical mappings and document handling
of new fields; preserve existing formatter options in legacy mode and reject conflicting options in server mode.
Dictionary subclasses preserve isinstance(result, dict), but change type(result) is dict; include this and custom
serializer compatibility in the major-release migration notes.
