![Logo](https://user-images.githubusercontent.com/2701938/108583516-c3576680-72ee-11eb-883f-2d9b52e74e45.png)

[![Build](https://github.com/ArangoDB-Community/python-arango/actions/workflows/build.yaml/badge.svg)](https://github.com/ArangoDB-Community/python-arango/actions/workflows/build.yaml)
[![CodeQL](https://github.com/ArangoDB-Community/python-arango/actions/workflows/codeql.yaml/badge.svg)](https://github.com/ArangoDB-Community/python-arango/actions/workflows/codeql.yaml)
[![codecov](https://codecov.io/gh/ArangoDB-Community/python-arango/branch/main/graph/badge.svg?token=M8zrjrzsUY)](https://codecov.io/gh/ArangoDB-Community/python-arango)
[![PyPI version](https://badge.fury.io/py/python-arango.svg)](https://badge.fury.io/py/python-arango)
[![GitHub license](https://img.shields.io/github/license/ArangoDB-Community/python-arango?color=brightgreen)](https://github.com/ArangoDB-Community/python-arango/blob/main/LICENSE)
![Python version](https://img.shields.io/badge/python-3.8%2B-blue)

# Python-Arango

Python driver for [ArangoDB](https://www.arangodb.com), a scalable multi-model
database natively supporting documents, graphs and search.

## Requirements

- ArangoDB version 3.9+
- Python version 3.8+

## Installation

```shell
pip install python-arango --upgrade
```

## Getting Started

Here is a simple usage example:

```python
from arango import ArangoClient

# Initialize the client for ArangoDB.
client = ArangoClient(hosts="http://localhost:8529")

# Connect to "_system" database as root user.
sys_db = client.db("_system", username="root", password="passwd")

# Create a new database named "test".
sys_db.create_database("test")

# Connect to "test" database as root user.
db = client.db("test", username="root", password="passwd")

# Create a new collection named "students".
students = db.create_collection("students")

# Add a hash index to the collection.
students.add_hash_index(fields=["name"], unique=True)

# Insert new documents into the collection.
students.insert({"name": "jane", "age": 39})
students.insert({"name": "josh", "age": 18})
students.insert({"name": "judy", "age": 21})

# Execute an AQL query and iterate through the result cursor.
cursor = db.aql.execute("FOR doc IN students RETURN doc")
student_names = [document["name"] for document in cursor]
```

Another example with [graphs](https://www.arangodb.com/docs/stable/graphs.html):

```python
from arango import ArangoClient

# Initialize the client for ArangoDB.
client = ArangoClient(hosts="http://localhost:8529")

# Connect to "test" database as root user.
db = client.db("test", username="root", password="passwd")

# Create a new graph named "school".
graph = db.create_graph("school")

# Create a new EnterpriseGraph [Enterprise Edition]
eegraph = db.create_graph(
    name="school",
    smart=True)

# Create vertex collections for the graph.
students = graph.create_vertex_collection("students")
lectures = graph.create_vertex_collection("lectures")

# Create an edge definition (relation) for the graph.
edges = graph.create_edge_definition(
    edge_collection="register",
    from_vertex_collections=["students"],
    to_vertex_collections=["lectures"]
)

# Insert vertex documents into "students" (from) vertex collection.
students.insert({"_key": "01", "full_name": "Anna Smith"})
students.insert({"_key": "02", "full_name": "Jake Clark"})
students.insert({"_key": "03", "full_name": "Lisa Jones"})

# Insert vertex documents into "lectures" (to) vertex collection.
lectures.insert({"_key": "MAT101", "title": "Calculus"})
lectures.insert({"_key": "STA101", "title": "Statistics"})
lectures.insert({"_key": "CSC101", "title": "Algorithms"})

# Insert edge documents into "register" edge collection.
edges.insert({"_from": "students/01", "_to": "lectures/MAT101"})
edges.insert({"_from": "students/01", "_to": "lectures/STA101"})
edges.insert({"_from": "students/01", "_to": "lectures/CSC101"})
edges.insert({"_from": "students/02", "_to": "lectures/MAT101"})
edges.insert({"_from": "students/02", "_to": "lectures/STA101"})
edges.insert({"_from": "students/03", "_to": "lectures/CSC101"})

# Traverse the graph in outbound direction, breadth-first.
result = graph.traverse(
    start_vertex="students/01",
    direction="outbound",
    strategy="breadthfirst"
)
```

Please see the [documentation](https://docs.python-arango.com) for more details.
