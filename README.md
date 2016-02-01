python-arango
=========

Python Driver for ArangoDB REST API

Overview
--------

Python-Arango is a Python driver for ArangoDB(<https://www.arangodb.com/>).

It is compatible with Python versions 2.7 and 3.4.

Installation
------------

-   Stable (supports up to ArangoDB version 2.7.0)

```bash
sudo pip install python-arango
```

-   Latest (supports up to ArangoDB version 2.7.0)

```bash
git clone https://github.com/Joowani/python-arango.git
cd python-arango
python2.7 setup.py install
```

Initialization
--------------

```python
from arango import Arango

# Initialize the API wrapper
a = Arango(host="localhost", port=8529)
```

Database Management
-------------------

```python
# List databases
a.databases(user_only=True)

# Create a new database
a.create_database("my_db")

# Delete a database
a.delete_database("my_db")

# Get the database object of the given name
a.database("my_db")  # equivalent to a.db("my_db")

# Retrieve information on the default ("_system") database
a.name           # equivalent to a.db("_system").name
a.collections    # equivalent to a.db("_system").collections
a.id             # equivalent to a.db("_system").id
a.file_path      # equivalent to a.db("_system").file_path
a.is_system      # equivalent to a.db("_system").is_system

# Retrieve information on a specific database
a.db("db01").name
a.db("db01").collections
a.db("db02").id
a.db("db03").file_path
a.db("db04").is_system

# Working with the default ("_system") database
a.create_collection("my_col")
a.aql_functions
a.*

# Working with a specific database
a.db("db01").create_collection("my_col")
a.db("db02").aql_functions
a.db("db03").*
```

Collection Management
---------------------

```python
my_db = a.db("my_db")

# List the collections in "my_db"
my_db.collections["user"]
my_db.collecitons["system"]
my_db.collections["all"]

# Create a collection
my_db.create_collection("new_col")

# Create an edge collection
my_db.create_collection("new_edge_col", is_edge=True)

# Rename a collection
my_db.rename_collection("new_col", "my_col")

# Delete a collection
my_db.delete_collection("my_col")

# Retrieve collection information
my_col = a.db("my_db").col("my_col")
len(my_col)
my_col.properties()
my_col.statistics()
my_col.revision()

# Update collection properties (only the modifiable ones)
my_col.wait_for_sync = False
my_col.journal_size = new_journal_size

# Load the collection into memory
my_col.load()
my_db.load_collection("my_col")

# Unload the collection from memory
my_col.unload()
my_db.unload_collection("my_col")

# Rotate the collection journal
my_col.rotate_journal()

# Return the checksum of the collection
my_col.checksum(with_rev=True, with_data=True)

# Delete all documents in the collection
my_col.truncate()
my_db.truncate_collection("my_col")

# Check if a document exists in the collection
"doc_key" in my_col
```

Document Management
-------------------

```python
my_col = a.db("my_db").col("my_col")

# Retrieve a document by its key
my_col.document("doc01")

# Create a new document ("_key" attribute is optional)
my_col.create_document({"_key": "doc01", "value": 1})

# Replace a document
my_col.replace_document("doc01", {"value": 2})

# Update a document
my_col.update_document("doc01", {"another_value": 3})

# Delete a document
my_col.delete_document("doc01")

# Iterate through the documents in a collection and update them
for doc in my_col:
    new_value = doc["value"] + 1
    my_col.update_document(doc["_key"], {"new_value": new_value})
```

Simple Queries
--------------

```python
# Return the first 5 documents in collection "my_col"
my_col.first(5)

# Return the last 3 documents
my_col.last(3)

# Return all documents (cursor generator object)
my_col.all()
list(my_col.all())

# Return a random document
my_col.any()

# Return first document whose "value" is 1
my_col.get_first_example({"value": 1})

# Return all documents whose "value" is 1
my_col.get_by_example({"value": 1})

# Update all documents whose "value" is 1 with a new attribute
my_col.update_by_example(
  {"value": 1}, new_value={"new_attr": 1}
)

# Return all documents within a radius around a given coordinate (requires geo-index)
my_col.within(latitude=100, longitude=20, radius=15)

# Return all documents near a given coordinate (requires geo-index)
my_col.near(latitude=100, longitude=20)

# Return all documents with fulltext match
my_col.fulltext("key", "foo,|bar")

# Look up documents by keys
my_col.lookup_by_keys(["key1", "key2", "key3"])

# Delete documents by keys
my_col.remove_by_keys(["key1", "key2", "key3"])
```

AQL Functions
-------------

```python
my_db = a.db("my_db")

# List the AQL functions defined in database "my_db"
my_db.aql_functions

# Create a new AQL function
my_db.create_aql_function(
  "myfunctions::temperature::ctof",
  "function (celsius) { return celsius * 1.8 + 32; }"
)

# Delete an AQL function
my_db.delete_aql_function("myfunctions::temperature::ctof")
```

AQL Queries
-----------

```python
# Retrieve the execution plan without actually executing it
my_db.explain_query("FOR doc IN my_col RETURN doc")

# Validate the AQL query without actually executing it
my_db.validate_query("FOR doc IN my_col RETURN doc")

# Execute the AQL query and iterate through the AQL cursor
cursor = my_db.execute_query(
  "FOR d IN my_col FILTER d.value == @val RETURN d",
  bind_vars={"val": "foobar"}
)
for doc in cursor:  # the cursor is deleted when the generator is exhausted
  print doc
```

Index Management
----------------

```python
my_col = a.collection("my_col")  # or a.col("mycol")

# List the indexes in collection "my_col"
my_col.indexes

# Create a unique hash index on attributes "attr1" and "attr2"
my_col.create_hash_index(fields=["attr1", "attr2"], unique=True)

# Create a cap constraint
my_col.create_cap_constraint(size=10, byte_size=40000)

# Create a unique skiplist index on attributes "attr1" and "attr2"
my_col.create_skiplist_index(["attr1", "attr2"], unique=True)

# Examples of creating a geo-spatial index on 1 (or 2) coordinate attributes
my_col.create_geo_index(fields=["coordinates"])
my_col.create_geo_index(fields=["longitude", "latitude"])

# Create a fulltext index on attribute "attr1"
my_col.create_fulltext_index(fields=["attr1"], min_length=10)
```

Graph Management
----------------

```python
my_db = a.db("my_db")

# List all the graphs in the database
my_db.graphs

# Create a new graph
my_graph = my_db.create_graph("my_graph")

# Create new vertex collections for a graph
my_db.create_collection("vcol01")
my_db.create_collection("vcol02")
my_graph.create_vertex_collection("vcol01")
my_graph.create_vertex_collection("vcol02")

# Create a new edge definition for a graph
my_db.create_collection("ecol01", is_edge=True)
my_graph.create_edge_definition(
  edge_collection="ecol01",
  from_vertex_collections=["vcol01"],
  to_vertex_collections=["vcol02"],
)

# Retrieve graph information
my_graph.properties()
my_graph.id
my_graph.revision
my_graph.edge_definitions
my_graph.vertex_collections
my_graph.orphan_collections
```

Vertex Management
-----------------

```python
# Create new vertices (if "_key" is not given it's auto-generated)
my_graph.create_vertex("vcol01", {"_key": "v01", "value": 1})
my_graph.create_vertex("vcol02", {"_key": "v01", "value": 1})

# Replace a vertex
my_graph.replace_vertex("vol01/v01", {"value": 2})

# Update a vertex
my_graph.update_vertex("vol02/v01", {"new_value": 3})

# Delete a vertex
my_graph.delete_vertex("vol01/v01")
```

Edge Management
---------------

```python
# Create a new edge
my_graph.create_edge(
  "ecol01",  # edge collection name
  {
    "_key": "e01",
    "_from": "vcol01/v01",  # must abide the edge definition
    "_to": "vcol02/v01",    # must abide the edge definition
    "foo": 1,
    "bar": 2,
  }
)

# Replace an edge
my_graph.replace_edge("ecol01/e01", {"baz": 2})

# Update an edge
my_graph.update_edge("ecol01/e01", {"foo": 3})

# Delete an edge
my_graph.delete_edge("ecol01/e01")
```

Graph Traversals
----------------

```python
my_graph = a.db("my_db").graph("my_graph")

# Execute a graph traversal
results = my_graph.execute_traversal(
  start_vertex="vcol01/v01",
  direction="outbound",
  strategy="depthfirst"
)

# Return the visited nodes in order
results.get("visited")

# Return the paths traversed in order
results.get("paths")
```

Batch Requests
--------------

```python
# NOTE: only CRUD methods for documents/vertices/edges are supported (WIP)

# Execute a batch request for managing documents
my_db.execute_batch([
    (
        my_col.create_document,             # method name
        [{"_key": "doc04", "value": 1}],    # args
        {"wait_for_sync": True}             # kwargs
    ),
    (
        my_col.update_document,
        ["doc01", {"value": 2}],
        {"wait_for_sync": True}
    ),
    (
        my_col.replace_document,
        ["doc02", {"new_value": 3}],
        {"wait_for_sync": True}
    ),
    (
        my_col.delete_document,
        ["doc03"],
        {"wait_for_sync": True}
    ),
    (
        my_col.create_document,
        [{"_key": "doc05", "value": 5}],
        {"wait_for_sync": True}
    ),
])

# Execute a batch request for managing vertexes
self.db.execute_batch([
    (
        my_graph.create_vertex,
        ["vcol01", {"_key": "v01", "value": 1}],
        {"wait_for_sync": True}
    ),
    (
        my_graph.create_vertex,
        ["vcol01", {"_key": "v02", "value": 2}],
        {"wait_for_sync": True}
    ),
    (
        my_graph.create_vertex,
        ["vcol01", {"_key": "v03", "value": 3}],
        {"wait_for_sync": True}
    ),
])
```

Transactions
------------

```python
# Execute a transaction
action = """
  function () {
      var db = require('internal').db;
      db.col01.save({ _key: 'doc01'});
      db.col02.save({ _key: 'doc02'});
      return 'success!';
  }
"""
res = my_db.execute_transaction(
    action=action,
    read_collections=["col01", "col02"],
    write_collections=["col01", "col02"],
    wait_for_sync=True,
    lock_timeout=10000
)
```

User Management
---------------
```python

# List all users
a.list_users()

# Create a new user
a.create_user("username", "password")

# Update a user
a.update_user("username", "password", change_password=True)

# Replace a user
a.replace_user("username", "password", extra={"foo": "bar"})

# Delete a user
a.delete_user("username")
```

Administration and Monitoring
-----------------------------
```python

# Read the global log from the server
a.get_log(level="debug")

# Reload the routing information
a.reload_routing()

# Return the server statistics
a.statistics()

# Return the role of the server in the cluster (if applicable)
a.role()
```

Miscellaneous Functions
-----------------------
```python

# Retrieve the versions of ArangoDB server and components
a.version

# Retrieve the required database version
a.required_database

# Retrieve the server time
a.server_time

# Retrieve the write-ahead log
a.write_ahead_log

# Flush the write-ahead log
a.flush_write_ahead_log(
    wait_for_sync=True, 
    wait_for_gc=True
)

# Configure the write-ahead log
a.set_write_ahead_log(
    allow_oversize=True,
    log_size=30000000,
    historic_logs=5,
    reserve_logs=5,
    throttle_wait=10000,
    throttle_when_pending=0
)

# Echo last request
a.echo()

# Shutdown the ArangoDB server
a.shutdown()


```

To Do
-----

1.  Tasks
2.  Async Result
3.  Endpoints
4.  Sharding


Running Tests
----------------------------------------------
The tests create temporary databases and users.
If a test fails in the middle dummy elements should be cleaned up (WIP). 

```bash
nosetests-2.7 -v
nosetests-3.4 -v

```
