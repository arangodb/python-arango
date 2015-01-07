python-arango
=============
[![Build Status](https://travis-ci.org/Joowani/python-arango.svg?branch=master)](https://travis-ci.org/Joowani/python-arango)

Driver for ArangoDB REST API

## Overview

python-arango is a driver for ArangoDB (https://www.arangodb.com/) REST API

## Installation

```bash
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
a.databases

# Obtaining database information
a.db("_system").name  # or just a.name (if db is not specified it defaults to "_system")
a.db("animals").collections
a.db("animals").id
a.db("animals").path
a.db("animals").is_system

# Managing collections
people = a.db("people")
people.collections  # list the collection names
people.add_collection("female")
people.rename_collection("female", "male")
people.remove_collection("male")

# Retrieving collection information
test_col = a.db("test_db").collection("test_col") # or a.db("people").col("test_col")
len(male)  # or male.count
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
test_col.contains(some_document_key)

# Managing AQL functions
people.aql_functions
people.add_aql_function(
  "myfunctions::temperature::celsiustofahrenheit",
  "function (celsius) { return celsius * 1.8 + 32; }"
)
people.remove_aql_function("myfunctions::temperature::celsiustofahrenheit")

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
test_col.update_by_example(               # update all documents whose "value" is 1 by the new value
  {"value": 1}, 
  new_value={"new_attr": 1}
)
# These queries require properly defined geo-index
test_col.within(
  latitude=100,
  longitude=20,
  radius=15,
)
test_col.near(
  latitude=100,
  longitude=20,
  radius=15,
)

# TODO document the rest

```


## Running System Tests
(Ensure ArangoDB is installed)
```bash
nosetests
```
