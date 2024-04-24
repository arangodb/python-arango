![Logo](https://user-images.githubusercontent.com/2701938/108583516-c3576680-72ee-11eb-883f-2d9b52e74e45.png)

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/arangodb/python-arango/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/arangodb/python-arango/tree/main)
[![CodeQL](https://github.com/arangodb/python-arango/actions/workflows/codeql.yaml/badge.svg)](https://github.com/arangodb/python-arango/actions/workflows/codeql.yaml)
[![Docs](https://github.com/arangodb/python-arango/actions/workflows/docs.yaml/badge.svg)](https://github.com/arangodb/python-arango/actions/workflows/docs.yaml)
[![Coverage Status](https://codecov.io/gh/arangodb/python-arango/branch/main/graph/badge.svg?token=M8zrjrzsUY)](https://codecov.io/gh/arangodb/python-arango)
[![Last commit](https://img.shields.io/github/last-commit/arangodb/python-arango)](https://github.com/arangodb/python-arango/commits/master)

[![PyPI version badge](https://img.shields.io/pypi/v/python-arango?color=3775A9&style=for-the-badge&logo=pypi&logoColor=FFD43B)](https://pypi.org/project/python-arango/)
[![Python versions badge](https://img.shields.io/badge/3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B&label=Python)](https://pypi.org/project/python-arango/)

[![License](https://img.shields.io/github/license/arangodb/python-arango?color=9E2165&style=for-the-badge)](https://github.com/arangodb/python-arango/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/static/v1?style=for-the-badge&label=code%20style&message=black&color=black)](https://github.com/psf/black)
[![Downloads](https://img.shields.io/pepy/dt/python-arango?style=for-the-badge&color=282661
)](https://pepy.tech/project/python-arango)

# Python-Arango

Python driver for [ArangoDB](https://www.arangodb.com), a scalable multi-model
database natively supporting documents, graphs and search.

## Requirements

- ArangoDB version 3.11+
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

# Add a persistent index to the collection.
students.add_persistent_index(fields=["name"], unique=True)

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

# Traverse the graph in outbound direction, breath-first.
query = """
    FOR v, e, p IN 1..3 OUTBOUND 'students/01' GRAPH 'school'
    OPTIONS { bfs: true, uniqueVertices: 'global' }
    RETURN {vertex: v, edge: e, path: p}
    """
cursor = db.aql.execute(query)
```

Please see the [documentation](https://docs.python-arango.com) for more details.
