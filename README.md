python-arango
=============
[![Build Status](https://travis-ci.org/Joowani/python-arango.svg?branch=master)](https://travis-ci.org/Joowani/python-arango)

Driver for ArangoDB REST API

## Overview

python-arango is a driver for ArangoDB (https://www.arangodb.com/) REST API

## Installation

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
test_db.aql_functions
test_db.add_aql_function(
  "myfunctions::temperature::celsiustofahrenheit",
  "function (celsius) { return celsius * 1.8 + 32; }"
)
test_db.remove_aql_function("myfunctions::temperature::celsiustofahrenheit")

# Managing collections
test_db = a.db("test_db")
test_db.collections  # list the collection names
test_db.add_collection("new_col")
test_db.rename_collection("new_col", "test_col")
test_db.remove_collection("test_col")

# Retrieving collection information
test_col = a.db("test_db").collection("test_col") # or a.db("test_db").col("test_col")
len(test_col)  # or test_col.count
test_col.properties
test_col.id
test_col.status
test_col.key_options
test_col.wait_for_sync
test_col.journal_size
test_col.is_system
test_col.is_edge
test_col.do_compact
test_col.figures
test_col.revision

# Collection specific methods
test_col.load()
test_col.unload()
test_col.rotate_journal()
test_col.checksum()
test_col.truncate()
test_col.contains("a_document_key")

# Managing indexes of a particular collection
test_col.indexes
test_col.add_hash_index(fields=["attr1", "attr2"], unique=True)
test_col.add_cap_constraint(size=10, byte_size=40000)
test_col.add_skiplist_index(["attr1", "attr2"], unique=True)
test_col.add_geo_index(fields=["coordinates"])
test_col.add_geo_index(fields=["longitude", "latitude"])
test_col.add_fulltext_index(fields=["attr1"], min_length=10)

# Managing documents in a particular collection
test_col = a.db("test_db").collection("test_col") 
test_col.get_document("doc01")
test_col.add_document({"_key": "doc01", "value": 1})
test_col.replace_document("doc01", {"value": 2})
test_col.update_document("doc01", {"another_value": 3})
test_col.remove_document("doc01")

# Simple collection-specific queries
test_col.first(5)                         # return the first 5 documents
test_col.last(3)                          # return the last 3 documents
test_col.all()                            # return all documents (generator object)
test_col.any()                            # return a random document
test_col.get_first_example({"value": 1})  # return first document whose "value" is 1
test_col.get_by_example({"value": 1})     # return all documents whose "value" is 1
test_col.update_by_example(               # update all documents whose "value" is 1 with the new value
  {"value": 1}, 
  new_value={"new_attr": 1}
)
test_col.within(latitude=100, longitude=20, radius=15)  # return all docs within (requires geo-index)
test_col.near(latitude=100, longitude=20, radius=15)    # return all docs near (requires geo-index)

# Managing Graphs
test_db = a.db("test_db")
test_db.graphs  # list all the graphs in the database
test_db.add_graph("new_graph")

new_graph = test_db.graph("new_graph")
# Adding vertex collections to a graph
test_db.add_collection("vertex_col_1")
test_db.add_collection("vertex_col_2")
new_graph.add_vertex_collection("vertex_col_1")
new_graph.add_vertex_collection("vertex_col_2")

# Adding an edge definition to a graph
test_db.add_collection("edge_col", is_edge=True)
new_graph.add_edge_definition(
  edge_collection="edge_col", 
  from_vertex_collections=["vertex_col_1"],
  to_vertex_collections=["vertex_col_2"],
)
# Retrieving information from a graph
new_graph.properties
new_graph.id
new_graph.revision
new_graph.edge_definitions
new_graph.vertex_collections
new_graph.orphan_collections

# TODO add more
```

## Running System Tests (requires ArangoDB on localhost)
```bash
nosetests
```
