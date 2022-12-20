---
layout: default
---
# Working with Documents

## Creating a Document

To create a new document, get a reference to the collection and call its `insert()` method, passing the object/document to be created in ArangoDB as a paramter.

```python
# Get a reference to the 'patients' collection
patients_col = db.collection(name="patients")

# Insert two new documents into the 'patients' collection
patients_col.insert({"name": "Jane", "age": 39})
patients_col.insert({"name": "John", "age": 18})
```
John's patient record is:
```json
{
  "_id": "patients/741603",
  "_rev": "_fQ2grGu---",
  "_key": "741603",
  "name": "John",
  "age": 18
}
```
## Patching a Document

To patch or partially update a document, call the `update()` method of the collection and pass the object/document as a parameter. The document must have a property named `_key` holding the unique key assigned to the document.

```python
# Patch John's patient record by adding a city property to the document
patients_col.update({ "_key": "741603", "city": "Cleveland" })
```
After the patching operation, John's document is:
```json
{
  "_id": "patients/741603",
  "_rev": "_fQ2h4TK---",
  "_key": "741603",
  "name": "John",
  "age": 18,
  "city": "Cleveland"
}
```
Notice that the record was patched by adding a `city` property to the document. All other properties remain the same.
## Replacing a Document

To replace or fully update a document, call the `replace()` method of the collection and pass the object/document that fully replaces thee existing document as a parameter. The document must have a property named `_key` holding the unique key assigned to the document.

```python
# Replace John's document
patients_col.replace({ "_key": "741603", "fullname": "John Doe", "age": 18, "city": "Cleveland" })
```
After the replacement operation, John's document is now:
```json
{
  "_id": "patients/741603",
  "_rev": "_fQ2uY3y---",
  "_key":"741603",
  "fullname": "John Doe",
  "age": 18,
  "city": "Cleveland"
}
```
Notice that the `name` property is now gone from John's document because it was not specified in the request when the document was fully replaced.
## Deleting a Document

To delete a document, call the `delete()` method of the collection and pass an document containing at least the `_key` attribute as a parameter.

```python
# Delete John's document
patients_col.delete({ "_key": "741603" })
```
