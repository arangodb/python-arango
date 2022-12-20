---
layout: default
---
# Working with Databases

## Connecting to Databases

To connect to a database, create an instance of `ArangoClient` which provides a connection to the database server. Then call its `db` method and pass the database name, user name and password as parameters.

```python
from arango import ArangoClient

# Initialize a client
client = ArangoClient(hosts="http://localhost:8529")

# Connect to the system database
sys_db = client.db("_system", username="root", password="qwerty")
```

## Retrieving a List of All Databases

To retrieve a list of all databases on an ArangoDB server, connect to the
`_system` database and call the `databases()` method.

```python
# Retrieve the names of all databases on the server as list of strings
db_list = sys_db.databases()
```

## Creating a Database

To create a new database, connect to the `_system` database and call
`create_database()`.

```python
# Create a new database named "test".
sys_db.create_database("test")

# Connect to "test" database as root user.
test_db = client.db("test", username="root", password="qwerty")
```

## Deleting a Database

To delete an existing database, connect to the `_system` database and call
`delete_database()` passing the name of the database to be deleted as a
parameter. The `_system` database cannot be deleted. Make sure to specify
the correct database name when you are deleting databases.

```python
# Delete the 'test' database
sys_db.delete_database("test")
```
