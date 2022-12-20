---
layout: default
---
# Working with Collections

## Retrieving a List of Collections

To retrieve a list of collections in a database, connect to the database and
call `collections()`.

```python
# Connect to the database
db = client.db(db_name, username=user_name, password=pass_word)

# Retrieve the list of collections
collection_list = db.collections()
```

## Creating a Collection

To create a new collection, connect to the database and call `create_collection()`.

```python
# Create a new collection for doctors
doctors_col = db.create_collection(name="doctors")

# Create another new collection for patients
patients_col = db.create_collection(name="patients")
```

## Deleting a Collection

To delete a collection, connect to the database and call `delete_collection()`,
passing the name of the collection to be deleted as a parameter. Make sure to
specify the correct collection name when you delete collections.

```python
# Delete the 'doctors' collection
db.delete_collection(name="doctors")
```
