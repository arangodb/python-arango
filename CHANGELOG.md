main
----

* Adding peak_memory_usage as a new property of AQL queries, available since ArangoDB 3.11.

* The explain method of AQL queries includes the "stats" field in the returned object. Note that the REST API returns
  it separately from the "plan" field, but for now we have to merge them together to ensure backward compatibility.
