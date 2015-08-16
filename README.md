Python-Arango
=========

Python Driver for ArangoDB REST API

Overview
--------

Python-Arango is a Python driver (2.7 and 3.4) for ArangoDB
(<https://www.arangodb.com/>)

Installation
------------

-   Stable (Supports ArangoDB Version 2.6)

```bash
sudo pip install python-arango
```

-   Latest (Supports ArangoDB Version 2.6)

```bash
git clone https://github.com/Joowani/python-arango.git
cd python-arango
python2.7 setup.py install
```

Initializing Connection
-----------------------

```python
from arango import Arango

# Initialize ArangoDB connection
conn = Arango(host="localhost", port=8529)
```

Databases
---------

```python
# List all databases
conn.databases
conn.databases["user"]
conn.databases["system"]

# Create a new database
conn.create_database("my_database")

# Delete a database
conn.delete_database("my_database")

# Retrieve information on the default ("_system") database
conn.name           # equivalent to conn.db("_system").name
conn.collections    # equivalent to conn.db("_system").collections
conn.id             # equivalent to conn.db("_system").id
conn.path           # equivalent to conn.db("_system").path
conn.is_system      # equivalent to conn.db("_system").is_system
conn.is_edge        # equivalent to conn.db("_system").is_edge
conn.is_volatile    # equivalent to conn.db("_system").is_volatile

# Retrieve information on a specific database
conn.db("db01").name
conn.db("db01").collections
conn.db("db02").id
conn.db("db03").path
conn.db("db04").is_system

# Working with the default ("_system") database
conn.create_collection("my_collection")
conn.aql_functions
conn.*

# Working with a specific database (e.g. "my_database")
conn.db("my_database").create_collection("my_collection")
conn.db("my_database").aql_functions
conn.db("my_database").*
```

User Management
---------------
```python

# List all users
conn.users

# Create a new user
conn.create_user("username", "password1")

# Update a user
conn.update_user("username", "password2", change_password=True)

# Replace a user
conn.replace_user("username", "password3")

# Delete a user
conn.delete_user("username")
```

Monitoring
----------
```python

# Retrieve global server log
conn.read_log(level="debug")

# Create a new user
conn.create_user("username", "password1")

# Update a user
conn.update_user("username", "password2", change_password=True)

# Replace a user
conn.replace_user("username", "password3")

# Delete a user
conn.delete_user("username")
```


AQL Functions
-------------

```python
my_database = conn.db("my_database")

# List the AQL functions defined in database "my_database"
my_database.aql_functions

# Create a new AQL function
my_database.create_aql_function(
  "myfunctions::temperature::ctof",
  "function (celsius) { return celsius * 1.8 + 32; }"
)

# Delete an AQL function
my_database.delete_aql_function("myfunctions::temperature::ctof")
```

AQL Queries
-----------

```python
# Retrieve the execution plan without actually executing it
my_database.explain_query("FOR doc IN my_collection RETURN doc")

# Validate the AQL query without actually executing it
my_database.validate_query("FOR doc IN my_collection RETURN doc")

# Execute the AQL query and iterate through the AQL cursor
cursor = my_database.execute_query(
  "FOR d IN my_collection FILTER d.value == @val RETURN d",
  bind_vars={"val": "foobar"}
)
for doc in cursor:  # the cursor is deleted when the generator is exhausted
  print doc
```

Collections
-----------

```python
my_database = conn.db("my_database")

# List the collections in "my_database"
my_database.collections
my_database.collections["user"]
my_database.collecitons["system"]
my_database.collections["all"]

# Create a collection
my_database.create_collection("new_collection")

# Create an edge collection
my_database.create_collection("new_ecollection", is_edge=True)

# Rename a collection
my_database.rename_collection("new_collection", "my_collection")

# Delete a collection
my_database.delete_collection("my_collection")

# Retrieve collection information
my_collection = conn.db("my_database").col("my_collection")
len(my_collection) == my_collection.count
my_collection.properties
my_collection.id
my_collection.status
my_collection.key_options
my_collection.wait_for_sync
my_collection.journal_size
my_collection.is_system
my_collection.is_edge
my_collection.do_compact
my_collection.figures
my_collection.revision

# Update collection properties (only the modifiable ones)
my_collection.wait_for_sync = False
my_collection.journal_size = new_journal_size

# Load the collection into memory
my_collection.load()

# Unload the collection from memory
my_collection.unload()

# Rotate the collection journal
my_collection.rotate_journal()

# Return the checksum of the collection
my_collection.checksum(with_rev=True, with_data=True)

# Delete all documents in the collection
my_collection.truncate()

# Check if a document exists in the collection
my_collection.contains("a_document_key")
"a_document_key" in my_collection
```

Indexes
-------

```python
my_collection = conn.collection("my_collection")  # or conn.col("mycol")

# List the indexes in collection "my_collection"
my_collection.indexes

# Create a unique hash index on attributes "attr1" and "attr2"
my_collection.create_hash_index(fields=["attr1", "attr2"], unique=True)

# Create a cap constraint
my_collection.create_cap_constraint(size=10, byte_size=40000)

# Create a unique skiplist index on attributes "attr1" and "attr2"
my_collection.create_skiplist_index(["attr1", "attr2"], unique=True)

# Examples of creating a geo-spatial index on 1 (or 2) coordinate attributes
my_collection.create_geo_index(fields=["coordinates"])
my_collection.create_geo_index(fields=["longitude", "latitude"])

# Create a fulltext index on attribute "attr1"
my_collection.create_fulltext_index(fields=["attr1"], min_length=10)
```

Documents
---------

```python
my_collection = conn.db("my_database").collection("my_collection")

# Retrieve a document by its key
my_collection.document("doc01")

# Create a new document ("_key" attribute is optional)
my_collection.create_document({"_key": "doc01", "value": 1})

# Replace a document
my_collection.replace_document("doc01", {"value": 2})

# Update a document
my_collection.update_document("doc01", {"another_value": 3})

# Delete a document
my_collection.delete_document("doc01")

# Iterate through the documents in a collection and update them
for doc in my_collection:
    new_value = doc["value"] + 1
    my_collection.update_document(doc["_key"], {"new_value": new_value})
```

Simple Queries (Collection-Specific)
------------------------------------

```python
# Return the first 5 documents in collection "my_collection"
my_collection.first(5)

# Return the last 3 documents
my_collection.last(3)

# Return all documents (cursor generator object)
my_collection.all()
list(my_collection.all())

# Return a random document
my_collection.any()

# Return first document whose "value" is 1
my_collection.get_first_example({"value": 1})

# Return all documents whose "value" is 1
my_collection.get_by_example({"value": 1})

# Update all documents whose "value" is 1 with a new attribute
my_collection.update_by_example(
  {"value": 1}, new_value={"new_attr": 1}
)

# Return all documents within a radius around a given coordinate (requires geo-index)
my_collection.within(latitude=100, longitude=20, radius=15)

# Return all documents near a given coordinate (requires geo-index)
my_collection.near(latitude=100, longitude=20)
```

Graphs
------

```python
my_database = conn.db("my_database")

# List all the graphs in the database
my_database.graphs

# Create a new graph
my_graph = my_database.create_graph("my_graph")

# Create new vertex collections to a graph
my_database.create_collection("vcol01")
my_database.create_collection("vcol02")
my_graph.create_vertex_collection("vcol01")
my_graph.create_vertex_collection("vcol02")

# Create a new edge definition to a graph
my_database.create_collection("ecol01", is_edge=True)
my_graph.create_edge_definition(
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
# Create new vertices (again if "_key" is not given it's auto-generated)
my_graph.create_vertex("vcol01", {"_key": "v01", "value": 1})
my_graph.create_vertex("vcol02", {"_key": "v01", "value": 1})

# Replace a vertex
my_graph.replace_vertex("vol01/v01", {"value": 2})

# Update a vertex
my_graph.update_vertex("vol02/v01", {"new_value": 3})

# Delete a vertex
my_graph.delete_vertex("vol01/v01")
```

Edges
-----

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
my_graph = conn.db("my_database").graph("my_graph")

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
# NOTE: only (create/update/replace/delete) methods for (documents/vertices/edges) are supported at the moment

# Execute a batch request for managing documents
my_database.execute_batch([
    (
        my_collection.create_document,                # method name
        [{"_key": "doc04", "value": 1}],    # args
        {"wait_for_sync": True}             # kwargs
    ),
    (
        my_collection.update_document,
        ["doc01", {"value": 2}],
        {"wait_for_sync": True}
    ),
    (
        my_collection.replace_document,
        ["doc02", {"new_value": 3}],
        {"wait_for_sync": True}
    ),
    (
        my_collection.delete_document,
        ["doc03"],
        {"wait_for_sync": True}
    ),
    (
        my_collection.create_document,
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
res = my_database.execute_transaction(
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
2.  Async Result
3.  Endpoints
4.  Sharding
5.  Misc. Functions

Running Tests (requires ArangoDB on localhost)
----------------------------------------------

```bash
nosetests -v
```
