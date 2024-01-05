__all__ = ["AQL", "AQLQueryCache"]

from numbers import Number
from typing import MutableMapping, Optional, Sequence, Union

from arango.api import ApiGroup
from arango.connection import Connection
from arango.cursor import Cursor
from arango.exceptions import (
    AQLCacheClearError,
    AQLCacheConfigureError,
    AQLCacheEntriesError,
    AQLCachePropertiesError,
    AQLFunctionCreateError,
    AQLFunctionDeleteError,
    AQLFunctionListError,
    AQLQueryClearError,
    AQLQueryExecuteError,
    AQLQueryExplainError,
    AQLQueryKillError,
    AQLQueryListError,
    AQLQueryRulesGetError,
    AQLQueryTrackingGetError,
    AQLQueryTrackingSetError,
    AQLQueryValidateError,
)
from arango.executor import ApiExecutor
from arango.formatter import (
    format_aql_cache,
    format_aql_query,
    format_aql_tracking,
    format_body,
    format_query_cache_entry,
    format_query_rule_item,
)
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import DataTypes, Json, Jsons


class AQLQueryCache(ApiGroup):
    """AQL Query Cache API wrapper."""

    def __repr__(self) -> str:
        return f"<AQLQueryCache in {self._conn.db_name}>"

    def properties(self) -> Result[Json]:
        """Return the query cache properties.

        :return: Query cache properties.
        :rtype: dict
        :raise arango.exceptions.AQLCachePropertiesError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/query-cache/properties")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise AQLCachePropertiesError(resp, request)
            return format_aql_cache(resp.body)

        return self._execute(request, response_handler)

    def configure(
        self,
        mode: Optional[str] = None,
        max_results: Optional[int] = None,
        max_results_size: Optional[int] = None,
        max_entry_size: Optional[int] = None,
        include_system: Optional[bool] = None,
    ) -> Result[Json]:
        """Configure the query cache properties.

        :param mode: Operation mode. Allowed values are "off", "on" and
            "demand".
        :type mode: str
        :param max_results: Max number of query results stored per
            database-specific cache.
        :type max_results: int
        :param max_results_size: Max cumulative size of query results stored
            per database-specific cache.
        :type max_results_size: int
        :param max_entry_size: Max entry size of each query result stored per
            database-specific cache.
        :type max_entry_size: int
        :param include_system: Store results of queries in system collections.
        :type include_system: bool
        :return: Query cache properties.
        :rtype: dict
        :raise arango.exceptions.AQLCacheConfigureError: If operation fails.
        """
        data: Json = {}
        if mode is not None:
            data["mode"] = mode
        if max_results is not None:
            data["maxResults"] = max_results
        if max_results_size is not None:
            data["maxResultsSize"] = max_results_size
        if max_entry_size is not None:
            data["maxEntrySize"] = max_entry_size
        if include_system is not None:
            data["includeSystem"] = include_system

        request = Request(
            method="put", endpoint="/_api/query-cache/properties", data=data
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise AQLCacheConfigureError(resp, request)
            return format_aql_cache(resp.body)

        return self._execute(request, response_handler)

    def entries(self) -> Result[Jsons]:
        """Return the query cache entries.

        :return: Query cache entries.
        :rtype: [dict]
        :raise AQLCacheEntriesError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/query-cache/entries")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise AQLCacheEntriesError(resp, request)
            return [format_query_cache_entry(entry) for entry in resp.body]

        return self._execute(request, response_handler)

    def clear(self) -> Result[bool]:
        """Clear the query cache.

        :return: True if query cache was cleared successfully.
        :rtype: bool
        :raise arango.exceptions.AQLCacheClearError: If operation fails.
        """
        request = Request(method="delete", endpoint="/_api/query-cache")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise AQLCacheClearError(resp, request)
            return True

        return self._execute(request, response_handler)


class AQL(ApiGroup):
    """AQL (ArangoDB Query Language) API wrapper.

    :param connection: HTTP connection.
    :param executor: API executor.
    """

    def __init__(self, connection: Connection, executor: ApiExecutor) -> None:
        super().__init__(connection, executor)

    def __repr__(self) -> str:
        return f"<AQL in {self._conn.db_name}>"

    @property
    def cache(self) -> AQLQueryCache:
        """Return the query cache API wrapper.

        :return: Query cache API wrapper.
        :rtype: arango.aql.AQLQueryCache
        """
        return AQLQueryCache(self._conn, self._executor)

    def explain(
        self,
        query: str,
        all_plans: bool = False,
        max_plans: Optional[int] = None,
        opt_rules: Optional[Sequence[str]] = None,
        bind_vars: Optional[MutableMapping[str, DataTypes]] = None,
    ) -> Result[Union[Json, Jsons]]:
        """Inspect the query and return its metadata without executing it.

        :param query: Query to inspect.
        :type query: str
        :param all_plans: If set to True, all possible execution plans are
            returned in the result. If set to False, only the optimal plan
            is returned.
        :type all_plans: bool
        :param max_plans: Total number of plans generated by the optimizer.
        :type max_plans: int
        :param opt_rules: List of optimizer rules.
        :type opt_rules: list
        :param bind_vars: Bind variables for the query.
        :type bind_vars: dict
        :return: Execution plan, or plans if **all_plans** was set to True.
        :rtype: dict | list
        :raise arango.exceptions.AQLQueryExplainError: If explain fails.
        """
        options: Json = {"allPlans": all_plans}
        if max_plans is not None:
            options["maxNumberOfPlans"] = max_plans
        if opt_rules is not None:
            options["optimizer"] = {"rules": opt_rules}

        data: Json = {"query": query, "options": options}
        if bind_vars is not None:
            data["bindVars"] = bind_vars

        request = Request(
            method="post",
            endpoint="/_api/explain",
            data=data,
        )

        def response_handler(resp: Response) -> Union[Json, Jsons]:
            if not resp.is_success:
                raise AQLQueryExplainError(resp, request)
            if "plan" in resp.body:
                result: Json = resp.body["plan"]
                if "stats" in resp.body:
                    result["stats"] = resp.body["stats"]
                return result
            else:
                results: Jsons = resp.body["plans"]
                if "stats" in resp.body:
                    # Although "plans" contains an array, "stats" is a single object.
                    # We need to duplicate "stats" for each plan in order to preserve
                    # the original structure.
                    for plan in results:
                        plan["stats"] = resp.body["stats"]
                return results

        return self._execute(request, response_handler)

    def validate(self, query: str) -> Result[Json]:
        """Parse and validate the query without executing it.

        :param query: Query to validate.
        :type query: str
        :return: Query details.
        :rtype: dict
        :raise arango.exceptions.AQLQueryValidateError: If validation fails.
        """
        request = Request(method="post", endpoint="/_api/query", data={"query": query})

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                body = format_body(resp.body)
                if "bindVars" in body:
                    body["bind_vars"] = body.pop("bindVars")
                return body

            raise AQLQueryValidateError(resp, request)

        return self._execute(request, response_handler)

    def execute(
        self,
        query: str,
        count: bool = False,
        batch_size: Optional[int] = None,
        ttl: Optional[Number] = None,
        bind_vars: Optional[MutableMapping[str, DataTypes]] = None,
        full_count: Optional[bool] = None,
        max_plans: Optional[int] = None,
        optimizer_rules: Optional[Sequence[str]] = None,
        cache: Optional[bool] = None,
        memory_limit: int = 0,
        fail_on_warning: Optional[bool] = None,
        profile: Optional[bool] = None,
        max_transaction_size: Optional[int] = None,
        max_warning_count: Optional[int] = None,
        intermediate_commit_count: Optional[int] = None,
        intermediate_commit_size: Optional[int] = None,
        satellite_sync_wait: Optional[int] = None,
        stream: Optional[bool] = None,
        skip_inaccessible_cols: Optional[bool] = None,
        max_runtime: Optional[Number] = None,
        fill_block_cache: Optional[bool] = None,
        allow_dirty_read: bool = False,
        allow_retry: bool = False,
        force_one_shard_attribute_value: Optional[str] = None,
    ) -> Result[Cursor]:
        """Execute the query and return the result cursor.

        :param query: Query to execute.
        :type query: str
        :param count: If set to True, the total document count is included in
            the result cursor.
        :type count: bool
        :param batch_size: Number of documents fetched by the cursor in one
            round trip.
        :type batch_size: int
        :param ttl: Server side time-to-live for the cursor in seconds.
        :type ttl: int
        :param bind_vars: Bind variables for the query.
        :type bind_vars: dict
        :param full_count: This parameter applies only to queries with LIMIT
            clauses. If set to True, the number of matched documents before
            the last LIMIT clause executed is included in the cursor. This is
            similar to MySQL SQL_CALC_FOUND_ROWS hint. Using this disables a
            few LIMIT optimizations and may lead to a longer query execution.
        :type full_count: bool
        :param max_plans: Max number of plans the optimizer generates.
        :type max_plans: int
        :param optimizer_rules: List of optimizer rules.
        :type optimizer_rules: [str]
        :param cache: If set to True, the query cache is used. The operation
            mode of the query cache must be set to "on" or "demand".
        :type cache: bool
        :param memory_limit: Max amount of memory the query is allowed to use
            in bytes. If the query goes over the limit, it fails with error
            "resource limit exceeded". Value 0 indicates no limit.
        :type memory_limit: int
        :param fail_on_warning: If set to True, the query throws an exception
            instead of producing a warning. This parameter can be used during
            development to catch issues early. If set to False, warnings are
            returned with the query result. There is a server configuration
            option "--query.fail-on-warning" for setting the default value for
            this behaviour, so it does not need to be set per-query.
        :type fail_on_warning: bool
        :param profile: Return additional profiling details in the cursor,
            unless the query cache is used.
        :type profile: bool
        :param max_transaction_size: Transaction size limit in bytes.
        :type max_transaction_size: int
        :param max_warning_count: Max number of warnings returned.
        :type max_warning_count: int
        :param intermediate_commit_count: Max number of operations after
            which an intermediate commit is performed automatically.
        :type intermediate_commit_count: int
        :param intermediate_commit_size: Max size of operations in bytes after
            which an intermediate commit is performed automatically.
        :type intermediate_commit_size: int
        :param satellite_sync_wait: Number of seconds in which the server must
            synchronize the satellite collections involved in the query. When
            the threshold is reached, the query is stopped. Available only for
            enterprise version of ArangoDB.
        :type satellite_sync_wait: int | float
        :param stream: If set to True, query is executed in streaming fashion:
            query result is not stored server-side but calculated on the fly.
            Note: long-running queries hold collection locks for as long as the
            cursor exists. If set to False, query is executed right away in its
            entirety. Results are either returned right away (if the result set
            is small enough), or stored server-side and accessible via cursors
            (while respecting the ttl). You should use this parameter only for
            short-running queries or without exclusive locks. Note: parameters
            **cache**, **count** and **full_count** do not work for streaming
            queries. Query statistics, warnings and profiling data are made
            available only after the query is finished. Default value is False.
        :type stream: bool
        :param skip_inaccessible_cols: If set to True, collections without user
            access are skipped, and query executes normally instead of raising
            an error. This helps certain use cases: a graph may contain several
            collections, and users with different access levels may execute the
            same query. This parameter lets you limit the result set by user
            access. Cannot be used in :doc:`transactions <transaction>` and is
            available only for enterprise version of ArangoDB. Default value is
            False.
        :type skip_inaccessible_cols: bool
        :param max_runtime: Query must be executed within this given timeout or
            it is killed. The value is specified in seconds. Default value
            is 0.0 (no timeout).
        :type max_runtime: int | float
        :param fill_block_cache: If set to true or not specified, this will
            make the query store the data it reads via the RocksDB storage
            engine in the RocksDB block cache. This is usually the desired
            behavior. The option can be set to false for queries that are
            known to either read a lot of data which would thrash the block
            cache, or for queries that read data which are known to be outside
            of the hot set. By setting the option to false, data read by the
            query will not make it into the RocksDB block cache if not already
            in there, thus leaving more room for the actual hot set.
        :type fill_block_cache: bool
        :param allow_dirty_read: Allow reads from followers in a cluster.
        :type allow_dirty_read: bool | None
        :param allow_retry: Make it possible to retry fetching the latest batch
            from a cursor.
        :type allow_retry: bool
        :param force_one_shard_attribute_value: (Enterprise Only) Explicitly set
            a shard key value that will be used during query snippet distribution
            to limit the query to a specific server in the cluster. This query option
            can be used in complex queries in case the query optimizer cannot
            automatically detect that the query can be limited to only a single
            server (e.g. in a disjoint smart graph case). If the option is set
            incorrectly, i.e. to a wrong shard key value, then the query may be
            shipped to a wrong DB server and may not return results
            (i.e. empty result set). Use at your own risk.
        :param force_one_shard_attribute_value: str | None
        :return: Result cursor.
        :rtype: arango.cursor.Cursor
        :raise arango.exceptions.AQLQueryExecuteError: If execute fails.
        """
        data: Json = {"query": query, "count": count}
        if batch_size is not None:
            data["batchSize"] = batch_size
        if ttl is not None:
            data["ttl"] = ttl
        if bind_vars is not None:
            data["bindVars"] = bind_vars
        if cache is not None:
            data["cache"] = cache
        if memory_limit is not None:
            data["memoryLimit"] = memory_limit

        options: Json = {}
        if full_count is not None:
            options["fullCount"] = full_count
        if fill_block_cache is not None:
            options["fillBlockCache"] = fill_block_cache
        if max_plans is not None:
            options["maxNumberOfPlans"] = max_plans
        if optimizer_rules is not None:
            options["optimizer"] = {"rules": optimizer_rules}
        if fail_on_warning is not None:
            options["failOnWarning"] = fail_on_warning
        if profile is not None:
            options["profile"] = profile
        if max_transaction_size is not None:
            options["maxTransactionSize"] = max_transaction_size
        if max_warning_count is not None:
            options["maxWarningCount"] = max_warning_count
        if intermediate_commit_count is not None:
            options["intermediateCommitCount"] = intermediate_commit_count
        if intermediate_commit_size is not None:
            options["intermediateCommitSize"] = intermediate_commit_size
        if satellite_sync_wait is not None:
            options["satelliteSyncWait"] = satellite_sync_wait
        if stream is not None:
            options["stream"] = stream
        if skip_inaccessible_cols is not None:
            options["skipInaccessibleCollections"] = skip_inaccessible_cols
        if max_runtime is not None:
            options["maxRuntime"] = max_runtime
        if allow_retry is not None:
            options["allowRetry"] = allow_retry
        if force_one_shard_attribute_value is not None:
            options["forceOneShardAttributeValue"] = force_one_shard_attribute_value

        if options:
            data["options"] = options
        data.update(options)

        request = Request(
            method="post",
            endpoint="/_api/cursor",
            data=data,
            headers={"x-arango-allow-dirty-read": "true"} if allow_dirty_read else None,
        )

        def response_handler(resp: Response) -> Cursor:
            if not resp.is_success:
                raise AQLQueryExecuteError(resp, request)
            return Cursor(self._conn, resp.body, allow_retry=allow_retry)

        return self._execute(request, response_handler)

    def kill(self, query_id: str) -> Result[bool]:
        """Kill a running query.

        :param query_id: Query ID.
        :type query_id: str
        :return: True if kill request was sent successfully.
        :rtype: bool
        :raise arango.exceptions.AQLQueryKillError: If the send fails.
        """
        request = Request(method="delete", endpoint=f"/_api/query/{query_id}")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise AQLQueryKillError(resp, request)
            return True

        return self._execute(request, response_handler)

    def queries(self) -> Result[Jsons]:
        """Return the currently running AQL queries.

        :return: Running AQL queries.
        :rtype: [dict]
        :raise arango.exceptions.AQLQueryListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/query/current")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise AQLQueryListError(resp, request)
            return [format_aql_query(q) for q in resp.body]

        return self._execute(request, response_handler)

    def slow_queries(self) -> Result[Jsons]:
        """Return a list of all slow AQL queries.

        :return: Slow AQL queries.
        :rtype: [dict]
        :raise arango.exceptions.AQLQueryListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/query/slow")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise AQLQueryListError(resp, request)
            return [format_aql_query(q) for q in resp.body]

        return self._execute(request, response_handler)

    def clear_slow_queries(self) -> Result[bool]:
        """Clear slow AQL queries.

        :return: True if slow queries were cleared successfully.
        :rtype: bool
        :raise arango.exceptions.AQLQueryClearError: If operation fails.
        """
        request = Request(method="delete", endpoint="/_api/query/slow")

        def response_handler(resp: Response) -> bool:
            if not resp.is_success:
                raise AQLQueryClearError(resp, request)
            return True

        return self._execute(request, response_handler)

    def tracking(self) -> Result[Json]:
        """Return AQL query tracking properties.

        :return: AQL query tracking properties.
        :rtype: dict
        :raise arango.exceptions.AQLQueryTrackingGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/query/properties")

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise AQLQueryTrackingGetError(resp, request)
            return format_aql_tracking(resp.body)

        return self._execute(request, response_handler)

    def set_tracking(
        self,
        enabled: Optional[bool] = None,
        max_slow_queries: Optional[int] = None,
        slow_query_threshold: Optional[int] = None,
        max_query_string_length: Optional[int] = None,
        track_bind_vars: Optional[bool] = None,
        track_slow_queries: Optional[bool] = None,
    ) -> Result[Json]:
        """Configure AQL query tracking properties

        :param enabled: Track queries if set to True.
        :type enabled: bool
        :param max_slow_queries: Max number of slow queries to track. Oldest entries
            are discarded first.
        :type max_slow_queries: int
        :param slow_query_threshold: Runtime threshold (in seconds) for treating a
            query as slow.
        :type slow_query_threshold: int
        :param max_query_string_length: Max query string length (in bytes) tracked.
        :type max_query_string_length: int
        :param track_bind_vars: If set to True, track bind variables used in queries.
        :type track_bind_vars: bool
        :param track_slow_queries: If set to True, track slow queries whose runtimes
            exceed **slow_query_threshold**. To use this, parameter **enabled** must
            be set to True.
        :type track_slow_queries: bool
        :return: Updated AQL query tracking properties.
        :rtype: dict
        :raise arango.exceptions.AQLQueryTrackingSetError: If operation fails.
        """
        data: Json = {}
        if enabled is not None:
            data["enabled"] = enabled
        if max_slow_queries is not None:
            data["maxSlowQueries"] = max_slow_queries
        if max_query_string_length is not None:
            data["maxQueryStringLength"] = max_query_string_length
        if slow_query_threshold is not None:
            data["slowQueryThreshold"] = slow_query_threshold
        if track_bind_vars is not None:
            data["trackBindVars"] = track_bind_vars
        if track_slow_queries is not None:
            data["trackSlowQueries"] = track_slow_queries

        request = Request(method="put", endpoint="/_api/query/properties", data=data)

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise AQLQueryTrackingSetError(resp, request)
            return format_aql_tracking(resp.body)

        return self._execute(request, response_handler)

    def functions(self) -> Result[Jsons]:
        """List the AQL functions defined in the database.

        :return: AQL functions.
        :rtype: [dict]
        :raise arango.exceptions.AQLFunctionListError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/aqlfunction")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise AQLFunctionListError(resp, request)

            functions: Jsons = resp.body["result"]
            for function in functions:
                if "isDeterministic" in function:
                    function["is_deterministic"] = function.pop("isDeterministic")

            return functions

        return self._execute(request, response_handler)

    def create_function(self, name: str, code: str) -> Result[Json]:
        """Create a new AQL function.

        :param name: AQL function name.
        :type name: str
        :param code: Function definition in Javascript.
        :type code: str
        :return: Whether the AQL function was newly created or an existing one
            was replaced.
        :rtype: dict
        :raise arango.exceptions.AQLFunctionCreateError: If create fails.
        """
        request = Request(
            method="post",
            endpoint="/_api/aqlfunction",
            data={"name": name, "code": code},
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise AQLFunctionCreateError(resp, request)
            return {"is_new": resp.body["isNewlyCreated"]}

        return self._execute(request, response_handler)

    def delete_function(
        self, name: str, group: bool = False, ignore_missing: bool = False
    ) -> Result[Union[bool, Json]]:
        """Delete an AQL function.

        :param name: AQL function name.
        :type name: str
        :param group: If set to True, value of parameter **name** is treated
            as a namespace prefix, and all functions in the namespace are
            deleted. If set to False, the value of **name** must be a fully
            qualified function name including any namespaces.
        :type group: bool
        :param ignore_missing: Do not raise an exception on missing function.
        :type ignore_missing: bool
        :return: Number of AQL functions deleted if operation was successful,
            False if function(s) was not found and **ignore_missing** was set
            to True.
        :rtype: dict | bool
        :raise arango.exceptions.AQLFunctionDeleteError: If delete fails.
        """
        request = Request(
            method="delete",
            endpoint=f"/_api/aqlfunction/{name}",
            params={"group": group},
        )

        def response_handler(resp: Response) -> Union[bool, Json]:
            if resp.error_code == 1582 and ignore_missing:
                return False
            if not resp.is_success:
                raise AQLFunctionDeleteError(resp, request)
            return {"deleted": resp.body["deletedCount"]}

        return self._execute(request, response_handler)

    def query_rules(self) -> Result[Jsons]:
        """Return the available optimizer rules for AQL queries

        :return: The available optimizer rules for AQL queries
        :rtype: dict
        :raise arango.exceptions.AQLQueryRulesGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/query/rules")

        def response_handler(resp: Response) -> Jsons:
            if not resp.is_success:
                raise AQLQueryRulesGetError(resp, request)

            rules: Jsons = resp.body
            items: Jsons = []
            for rule in rules:
                items.append(format_query_rule_item(rule))
            return items

        return self._execute(request, response_handler)
