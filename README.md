python-arango
=============
[![Build Status](https://travis-ci.org/Joowani/python-arango.svg?branch=master)](https://travis-ci.org/Joowani/python-arango)

Driver for ArangoDB REST API

## Overview

python-arango is a driver for ArangoDB (https://www.arangodb.com/) REST API

## Installation (will be in PyPi soon)

```bash
git clone https://github.com/Joowani/python-arango.git
cd python-arango
python2.7 setup.py install
```

## Initializing ArangoDB Connection
```python
from arango import Arango

# Initialize ArangoDB connection
a = Arango(host="localhost", port=8529)
```

## Databases
```python
# List the database names
a.databases["user"]
a.databases["system"]

# Retrieve database information
a.db("_system").name
a.name  # if db is not specified default database "_system" is used
a.db("db01").collections
a.db("db02").id
a.db("db03").path
a.db("dbXX").is_system
```

## AQL Functions
```python
my_db = a.db("my_db")
# List the AQL functions that's defined in databse "my_db"
my_db.aql_functions
# Add a new AQL function
my_db.add_aql_function(
  "myfunctions::temperature::ctof",
  "function (celsius) { return celsius * 1.8 + 32; }"
)
# Remove a AQL function
my_db.remove_aql_function("myfunctions::temperature::ctof")
```

## AQL Queries
```python
# Retrieve the execution plan without executing it
my_db.explain_query("FOR doc IN my_col doc")
# Validate the AQL query without executing it
my_db.validate_query("FOR doc IN my_col doc")
# Execute the AQL query and iterate through the AQL cursor
cursor = my_db.execute_query(
  "FOR d IN my_col FILTER d.value == @val RETURN d",
  bind_vars={"val": "foobar"}
)
for doc in cursor:  # the cursor is deleted when the generator is exhausted
  print doc
```

## Collections
```python
my_db = a.db("my_db")
# List the collection names in "my_db"
my_db.collections
# Add a new collection
my_db.add_collection("new_col")
# Add a new edge collection
my_db.add_collection("new_ecol", is_edge=True)
# Rename a collection
my_db.rename_collection("new_col", "my_col")
# Remove a collection from the database
my_db.remove_collection("my_col")

# Retrieve collection information
my_col = a.db("my_db").collection("my_col")
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

# Load the collection into memory
my_col.load()
# Unload the collection from memory
my_col.unload()
# Rotate the collection journal
my_col.rotate_journal()
# Return the checksum of the collection
my_col.checksum()
# Remove all documents in the collection
my_col.truncate()
# Check if a document exists in the collection
my_col.contains("a_document_key")
"a_document_key" in my_col
```

## Indexes

```python
my_col = a.collection("my_col")

# List all the indexes in collection "my_col"
my_col.indexes

# Add a unique hash index attributes "attr1" and "attr2"
my_col.add_hash_index(fields=["attr1", "attr2"], unique=True)

# Add a cap constraint
my_col.add_cap_constraint(size=10, byte_size=40000)

# Add a unique skiplist index on attributes "attr1" and "attr2"
my_col.add_skiplist_index(["attr1", "attr2"], unique=True)

# Examples of adding a geo-spatial index on 1 or 2 attributes
my_col.add_geo_index(fields=["coordinates"])
my_col.add_geo_index(fields=["longitude", "latitude"])

# Add a fulltext index on attribute "attr1"
my_col.add_fulltext_index(fields=["attr1"], min_length=10)
```

## Documents

```python
# Managing documents in a particular collection
my_col = a.db("my_db").collection("my_col")
my_col.get_document("doc01")
my_col.add_document({"_key": "doc01", "value": 1})
my_col.replace_document("doc01", {"value": 2})
my_col.update_document("doc01", {"another_value": 3})
my_col.remove_document("doc01")
for doc in my_col:
    new_value = doc["value"] + 1
    my_col.update_document(doc["_key"], {"new_value": new_value})
```

# Simple collection-specific queries
my_col.first(5)                         # return the first 5 documents
my_col.last(3)                          # return the last 3 documents
my_col.all()                            # return all documents (generator object)
my_col.any()                            # return a random document
my_col.get_first_example({"value": 1})  # return first document whose "value" is 1
my_col.get_by_example({"value": 1})     # return all documents whose "value" is 1
my_col.update_by_example(               # update all documents whose "value" is 1 with the new value
  {"value": 1},
  new_value={"new_attr": 1}
)
my_col.within(latitude=100, longitude=20, radius=15)  # return all docs within (requires geo-index)
my_col.near(latitude=100, longitude=20, radius=15)    # return all docs near (requires geo-index)

# Managing Graphs
my_db = a.db("my_db")
my_db.graphs  # list all the graphs in the database
my_graph = my_db.add_graph("my_graph")

# Adding vertex collections to a graph
my_db.add_collection("vcol01")
my_db.add_collection("vcol02")
my_graph.add_vertex_collection("vcol01")
my_graph.add_vertex_collection("vcol02")

# Adding an edge definition to a graph
my_db.add_collection("ecol01", is_edge=True)
my_graph.add_edge_definition(
  edge_collection="ecol01",
  from_vertex_collections=["vcol01"],
  to_vertex_collections=["vcol02"],
)
# Retrieving information from a graph
my_graph.properties
my_graph.id
my_graph.revision
my_graph.edge_definitions
my_graph.vertex_collections
my_graph.orphan_collections

# Managing vertices (needs valid vertex collections)
my_graph.add_vertex("vcol01", {"_key": "v01", "value": 1})
my_graph.add_vertex("vcol02", {"_key": "v01", "value": 1})
my_graph.replace_vertex("vol01/v01", {"value": 2})
my_graph.update_vertex("vol02/v01", {"new_value": 3})
my_graph.remove_vertex("vol01/v01")

# Managing edges (needs valid vertex and edge collections)
my_graph.add_edge(
  "ecol01",
  {
    "_key": "e01",
    "_from": "vcol01/v01",  # must abide the edge definition
    "_to": "vcol02/v01",    # must abide the edge definition
    "value": 1,
  }
)
my_graph.replace_edge("ecol01/e01", {"new_value": 2})
my_graph.update_edge("ecol01/e01", {"value": 3})
my_graph.remove_edge("ecol01/e01")

# Graph traversals
results = my_graph.execute_traversal(
  start_vertex="vcol01/v01",
  direction="outbound",
  strategy="depthfirst"
)
results.get("visited")
results.get("paths")

# Batch Requests (only add, update, replace and remove methods are supported atm)
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

## Running System Tests (requires ArangoDB on localhost)
```bash
nosetests
```
