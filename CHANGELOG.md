main
----

* Added new per-operation option `refillIndexCache` to write operations:

  - single-document write operations (insert, replace, update, delete)
  - multi-document write operations (insert_many, replace_many, update_many, delete_many)

  If the option is set to `True`, new entries are added to in-memory index caches if
  document operations affect the edge index or cache-enabled persistent indexes. Every
  currently running transaction will keep track of which in-memory index cache entries
  were invalidated by the transaction, and will try to (re-)fill them later.

  Example:
  ```python
  collection.insert({"foo": "bar"}, refillIndexCaches=True)
  db.aql.execute("INSERT {foo: bar} INTO collection OPTIONS { refillIndexCaches: true }")
  ```

7.5.9
-----

* Added cache and primaryKeyCache parameters to the inverted index API.

* Added allow_retry query parameter, making it possible to retry fetching the latest batch from a cursor.

* Added OverloadControlDatabase, enabling the client to react effectively to potential server overloads.

* The db.version() now has a new optional parameter "details" that can be used to return additional information about
  the server version. The default is still false, so the old behavior is preserved.

* Added peak_memory_usage as a new property of AQL queries, available since ArangoDB 3.11.

* The explain method of AQL queries includes the "stats" field in the returned object. Note that the REST API returns
  it separately from the "plan" field, but for now we have to merge them together to ensure backward compatibility.
