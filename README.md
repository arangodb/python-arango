# python-arango

Python driver for [ArangoDB](https://www.arangodb.com).

## Requirements

Python 3.6+ and ArangoDB 3.7+  

## Installation

```shell
pip install python-arango
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

Here is another example with graphs:

```python
from arango import ArangoClient

# Initialize the client for ArangoDB.
client = ArangoClient(hosts="http://localhost:8529")

# Connect to "test" database as root user.
db = client.db("test", username="root", password="passwd")

# Create a new graph named "school".
graph = db.create_graph("school")

# Create vertex collections for the graph.
students = graph.create_vertex_collection("students")
lectures = graph.create_vertex_collection("lectures")

# Create an edge definition (relation) for the graph.
register = graph.create_edge_definition(
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
register.insert({"_from": "students/01", "_to": "lectures/MAT101"})
register.insert({"_from": "students/01", "_to": "lectures/STA101"})
register.insert({"_from": "students/01", "_to": "lectures/CSC101"})
register.insert({"_from": "students/02", "_to": "lectures/MAT101"})
register.insert({"_from": "students/02", "_to": "lectures/STA101"})
register.insert({"_from": "students/03", "_to": "lectures/CSC101"})

# Traverse the graph in outbound direction, breadth-first.
result = graph.traverse(
    start_vertex="students/01",
    direction="outbound",
    strategy="breadthfirst"
)
```

Please see [documentation](http://python-driver-for-arangodb.readthedocs.io/en/master/index.html) 
for more details.
