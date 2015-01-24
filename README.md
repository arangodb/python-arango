py-arango
=========

[![Build
Status](https://travis-ci.org/Joowani/py-arango.svg?branch=master)](https://travis-ci.org/Joowani/py-arango)
[![Documentation
Status](https://readthedocs.org/projects/py-arango/badge/?version=latest)](https://readthedocs.org/projects/py-arango/?badge=latest)

Driver for ArangoDB REST API

Overview
--------

py-arango is a Python (2.7, 3.4) driver for ArangoDB
(<https://www.arangodb.com/>)

Documentation
-------------

<http://py-arango.readthedocs.org/en/latest/>

Installation
------------

-   Stable

```bash
sudo pip install py-arango
```

-   Latest

```bash
git clone https://github.com/Joowani/py-arango.git
cd py-arango
python2.7 setup.py install
```

Initializing Connection
-----------------------

```python
from arango import Arango

# Initialize ArangoDB connection
a = Arango(host="localhost", port=8529)
```

Databases
---------

```python
# List the database names
a.databases
a.databases["user"]
a.databases["system"]

# Get information on the default database ("_system")
a.name          # equivalent to a.db("_system").name
a.collections   # equivalent to a.db("_system").collections
a.id            # equivalent to a.db("_system").id
a.path          # equivalent to a.db("_system").path
a.is_system     # equivalent to a.db("_system").is_system

# Get information on a specific database
a.db("db01").collections
a.db("db02").id
a.db("db03").path
a.db("dbXX").is_system

# Create a new database
a.add_database("my_db")

# Remove a database
a.remove_database("my_db")

# Working with database "_system"
a.add_collection("my_col")
a.col("my_col").add_document({"value" : 1})
a.{whatever}

# Working with database "my_db"
a.db("my_db").add_collection("my_col")
a.db("my_db").col("my_col").add_document({"value": 1})
a.db("my_db").{whatever}
```

AQL Functions
-------------

```python
my_db = a.db("my_db")

# List the AQL functions defined in database "my_db"
my_db.aql_functions

# Add a new AQL function
my_db.add_aql_function(
  "myfunctions::temperature::ctof",
  "function (celsius) { return celsius * 1.8 + 32; }"
)

# Remove an AQL function
my_db.remove_aql_function("myfunctions::temperature::ctof")
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

Collections
-----------

```python
my_db = a.db("my_db")

# List the collection names in "my_db"
my_db.collections
my_db.collections["user"]
my_db.collecitons["system"]
my_db.collections["all"]

# Add a new collection
my_db.add_collection("new_col")

# Add a new edge collection
my_db.add_collection("new_ecol", is_edge=True)

# Rename a collection
my_db.rename_collection("new_col", "my_col")

# Remove a collection from the database
my_db.remove_collection("my_col")

# Retrieve collection information
my_col = a.db("my_db").col("my_col")
len(my_col) == my_col.count
my_col.properties
my_col.id
my_col.status
my_col.key_options
my_col.wait_for_sync
my_col.journal_size
my_col.is_system
my_col.is_edge
my_col.do_compact
my_col.figures
my_col.revision

# Modify collection properties (only the modifiable ones)
my_col.wait_for_sync = False
my_col.journal_size = new_journal_size

# Load the collection into memory
my_col.load()

# Unload the collection from memory
my_col.unload()

# Rotate the collection journal
my_col.rotate_journal()

# Return the checksum of the collection
my_col.checksum(with_rev=True, with_data=True)

# Remove all documents in the collection
my_col.truncate()

# Check if a document exists in the collection
my_col.contains("a_document_key")
"a_document_key" in my_col
```

Indexes
-------

```python
my_col = a.collection("my_col")  # or a.col("mycol")

# List the indexes in collection "my_col"
my_col.indexes

# Add a unique hash index on attributes "attr1" and "attr2"
my_col.add_hash_index(fields=["attr1", "attr2"], unique=True)

# Add a cap constraint
my_col.add_cap_constraint(size=10, byte_size=40000)

# Add a unique skiplist index on attributes "attr1" and "attr2"
my_col.add_skiplist_index(["attr1", "attr2"], unique=True)

# Examples of adding a geo-spatial index on 1 (or 2) coordinate attributes
my_col.add_geo_index(fields=["coordinates"])
my_col.add_geo_index(fields=["longitude", "latitude"])

# Add a fulltext index on attribute "attr1"
my_col.add_fulltext_index(fields=["attr1"], min_length=10)
```

Documents
---------

```python
my_col = a.db("my_db").collection("my_col")

# Retrieve a document by its key
my_col.get_document("doc01")

# Add a new document ("_key" attribute is optional)
my_col.add_document({"_key": "doc01", "value": 1})

# Replace a document
my_col.replace_document("doc01", {"value": 2})

# Update a document
my_col.update_document("doc01", {"another_value": 3})

# Remove a document
my_col.remove_document("doc01")

# Iterate through the documents in a collection and update them
for doc in my_col:
    new_value = doc["value"] + 1
    my_col.update_document(doc["_key"], {"new_value": new_value})
```

Simple Queries (Collection-Specific)
------------------------------------

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
```

Graphs
------

```python
my_db = a.db("my_db")

# List all the graphs in the database
my_db.graphs

# Add a new graph
my_graph = my_db.add_graph("my_graph")

# Add new vertex collections to a graph
my_db.add_collection("vcol01")
my_db.add_collection("vcol02")
my_graph.add_vertex_collection("vcol01")
my_graph.add_vertex_collection("vcol02")

# Add a new edge definition to a graph
my_db.add_collection("ecol01", is_edge=True)
my_graph.add_edge_definition(
  edge_collection="ecol01",
  from_vertex_collections=["vcol01"],
  to_vertex_collections=["vcol02"],
)

# Retrieve graph information
my_graph.properties
my_graph.id
my_graph.revision
my_graph.edge_definitions
my_graph.vertex_collections
my_graph.orphan_collections
```

Vertices
--------

```python
# Add new vertices (again if "_key" is not given it's auto-generated)
my_graph.add_vertex("vcol01", {"_key": "v01", "value": 1})
my_graph.add_vertex("vcol02", {"_key": "v01", "value": 1})

# Replace a vertex
my_graph.replace_vertex("vol01/v01", {"value": 2})

# Update a vertex
my_graph.update_vertex("vol02/v01", {"new_value": 3})

# Remove a vertex
my_graph.remove_vertex("vol01/v01")
```

Edges
-----

```python
# Add a new edge
my_graph.add_edge(
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

# Remove an edge
my_graph.remove_edge("ecol01/e01")
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
# NOTE: only (add/update/replace/remove) methods for (documents/vertices/edges) are supported at the moment

# Execute a batch request for managing documents
my_db.execute_batch([
    (
        my_col.add_document,                # method name
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
        my_col.remove_document,
        ["doc03"],
        {"wait_for_sync": True}
    ),
    (
        my_col.add_document,
        [{"_key": "doc05", "value": 5}],
        {"wait_for_sync": True}
    ),
])

# Execute a batch request for managing vertexes
self.db.execute_batch([
    (
        my_graph.add_vertex,
        ["vcol01", {"_key": "v01", "value": 1}],
        {"wait_for_sync": True}
    ),
    (
        my_graph.add_vertex,
        ["vcol01", {"_key": "v02", "value": 2}],
        {"wait_for_sync": True}
    ),
    (
        my_graph.add_vertex,
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

To Do
-----

1.  Tasks
2.  Monitoring
3.  User Management
4.  Async Result
5.  Endpoints
6.  Sharding
7.  Misc. Functions
8.  General Handling

Running Tests (requires ArangoDB on localhost)
----------------------------------------------

```bash
nosetests
```
