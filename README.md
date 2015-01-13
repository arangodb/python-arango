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

## Usage

```python
from arango import Arango

# Initialize ArangoDB connection
a = Arango(host="localhost", port=8529)

# Getting the version of ArangoDB
a.version

# Getting the names of the databases
a.databases["user"]
a.databases["system"]

# Obtaining database information
a.db("_system").name  # or just a.name (if db is not specified it defaults to "_system")
a.db("animals").collections
a.db("animals").id
a.db("animals").path
a.db("animals").is_system

# Managing AQL functions
my_db.aql_functions
my_db.add_aql_function(
  "myfunctions::temperature::celsiustofahrenheit",
  "function (celsius) { return celsius * 1.8 + 32; }"
)
my_db.remove_aql_function("myfunctions::temperature::celsiustofahrenheit")

# Queries
my_db.explain_query("FOR doc IN my_col doc")
my_db.validate_query("FOR doc IN my_col doc")
cursor = my_db.execute_query(
  "FOR d IN my_col FILTER d.value == @val RETURN d",
  bind_vars={"val": "foobar"}
)
for doc in cursor:
  print doc

# Managing collections
my_db = a.db("my_db")
my_db.collections  # list the collection names
my_db.add_collection("new_col")
my_db.rename_collection("new_col", "my_col")
my_db.remove_collection("my_col")

# Retrieving collection information
my_col = a.db("my_db").collection("my_col") # or a.db("my_db").col("my_col")
len(my_col)  # or my_col.count
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

# Collection specific methods
my_col.load()
my_col.unload()
my_col.rotate_journal()
my_col.checksum()
my_col.truncate()
my_col.contains("a_document_key")

# Managing indexes of a particular collection
my_col.indexes
my_col.add_hash_index(fields=["attr1", "attr2"], unique=True)
my_col.add_cap_constraint(size=10, byte_size=40000)
my_col.add_skiplist_index(["attr1", "attr2"], unique=True)
my_col.add_geo_index(fields=["coordinates"])
my_col.add_geo_index(fields=["longitude", "latitude"])
my_col.add_fulltext_index(fields=["attr1"], min_length=10)

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
my_db.add_graph("my_graph")

my_graph = my_db.graph("my_graph")
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

# Batch Requests (only add, update, replace and remove methods supported)
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
