from typing import Any, Sequence

from arango.typings import Headers, Json


def verify_format(_: Any, res: Json) -> Json:
    return res


def format_body(body: Json) -> Json:
    """Format generic response body.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    body.pop("error", None)
    body.pop("code", None)
    return body


def format_index(body: Json, formatter: bool = True) -> Json:
    """Format index data.

    :param body: Input body.
    :type body: dict
    :param formatter: Convert (most) keys to snake_case.
    :type formatter: bool
    :return: Formatted body.
    :rtype: dict
    """
    if not formatter:
        body.pop("code")
        body.pop("error")
        body["id"] = body["id"].split("/", 1)[-1]
        return body

    result = {"id": body["id"].split("/", 1)[-1], "fields": body["fields"]}
    if "type" in body:
        result["type"] = body["type"]
    if "name" in body:
        result["name"] = body["name"]
    if "deduplicate" in body:
        result["deduplicate"] = body["deduplicate"]
    if "sparse" in body:
        result["sparse"] = body["sparse"]
    if "unique" in body:
        result["unique"] = body["unique"]
    if "minLength" in body:
        result["min_length"] = body["minLength"]
    if "geoJson" in body:
        result["geo_json"] = body["geoJson"]
    if "ignoreNull" in body:
        result["ignore_none"] = body["ignoreNull"]
    if "selectivityEstimate" in body:
        result["selectivity"] = body["selectivityEstimate"]
    if "isNewlyCreated" in body:
        result["new"] = body["isNewlyCreated"]
    if "expireAfter" in body:
        result["expiry_time"] = body["expireAfter"]
    if "inBackground" in body:
        result["in_background"] = body["inBackground"]
    if "bestIndexedLevel" in body:
        result["best_indexed_level"] = body["bestIndexedLevel"]
    if "worstIndexedLevel" in body:
        result["worst_indexed_level"] = body["worstIndexedLevel"]
    if "maxNumCoverCells" in body:
        result["max_num_cover_cells"] = body["maxNumCoverCells"]
    if "storedValues" in body:
        result["storedValues"] = body["storedValues"]
    if "cacheEnabled" in body:
        result["cacheEnabled"] = body["cacheEnabled"]
    if "legacyPolygons" in body:
        result["legacyPolygons"] = body["legacyPolygons"]
    if "estimates" in body:
        result["estimates"] = body["estimates"]
    if "analyzer" in body:
        result["analyzer"] = body["analyzer"]
    if "cleanupIntervalStep" in body:
        result["cleanup_interval_step"] = body["cleanupIntervalStep"]
        if "commitIntervalMsec" in body:
            result["commit_interval_msec"] = body["commitIntervalMsec"]
    if "consolidationIntervalMsec" in body:
        result["consolidation_interval_msec"] = body["consolidationIntervalMsec"]
    if "consolidationPolicy" in body:
        result["consolidation_policy"] = format_view_consolidation_policy(
            body["consolidationPolicy"]
        )
    if "features" in body:
        result["features"] = body["features"]
    if "includeAllFields" in body:
        result["include_all_fields"] = body["includeAllFields"]
    if "primarySort" in body:
        result["primary_sort"] = body["primarySort"]
    if "searchField" in body:
        result["search_field"] = body["searchField"]
    if "trackListPositions" in body:
        result["track_list_positions"] = body["trackListPositions"]
    if "version" in body:
        result["version"] = body["version"]
    if "cache" in body:
        result["cache"] = body["cache"]
    if "primaryKeyCache" in body:
        result["primaryKeyCache"] = body["primaryKeyCache"]
    if "writebufferIdle" in body:
        result["writebuffer_idle"] = body["writebufferIdle"]
    if "writebufferActive" in body:
        result["writebuffer_active"] = body["writebufferActive"]
    if "writebufferSizeMax" in body:
        result["writebuffer_max_size"] = body["writebufferSizeMax"]
    if "fieldValueTypes" in body:
        result["field_value_types"] = body["fieldValueTypes"]

    # Introduced in 3.12 EE
    if "optimizeTopK" in body:
        result["optimizeTopK"] = body["optimizeTopK"]

    return verify_format(body, result)


def format_key_options(body: Json) -> Json:
    """Format collection key options data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "type" in body:
        result["key_generator"] = body["type"]
    if "increment" in body:
        result["key_increment"] = body["increment"]
    if "offset" in body:
        result["key_offset"] = body["offset"]
    if "allowUserKeys" in body:
        result["user_keys"] = body["allowUserKeys"]
    if "lastValue" in body:
        result["key_last_value"] = body["lastValue"]

    return verify_format(body, result)


def format_database(body: Json) -> Json:
    """Format databases info.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "id" in body:
        result["id"] = body["id"]
    if "name" in body:
        result["name"] = body["name"]
    if "path" in body:
        result["path"] = body["path"]
    if "system" in body:
        result["system"] = body["system"]
    if "isSystem" in body:
        result["system"] = body["isSystem"]

    # Cluster only
    if "sharding" in body:
        result["sharding"] = body["sharding"]
    if "replicationFactor" in body:
        result["replication_factor"] = body["replicationFactor"]
    if "writeConcern" in body:
        result["write_concern"] = body["writeConcern"]
    if "replicationVersion" in body:
        result["replication_version"] = body["replicationVersion"]

    return verify_format(body, result)


def format_collection(body: Json) -> Json:
    """Format collection data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "id" in body:
        result["id"] = body["id"]
    if "objectId" in body:
        result["object_id"] = body["objectId"]
    if "name" in body:
        result["name"] = body["name"]
    if "isSystem" in body:
        result["system"] = body["isSystem"]
    if "isSmart" in body:
        result["smart"] = body["isSmart"]
    if "type" in body:
        result["type"] = body["type"]
        result["edge"] = body["type"] == 3
    if "waitForSync" in body:
        result["sync"] = body["waitForSync"]

    if "status" in body:
        result["status"] = body["status"]
    if "statusString" in body:
        result["status_string"] = body["statusString"]
    if "globallyUniqueId" in body:
        result["global_id"] = body["globallyUniqueId"]
    if "cacheEnabled" in body:
        result["cache"] = body["cacheEnabled"]
    if "replicationFactor" in body:
        result["replication_factor"] = body["replicationFactor"]
    if "minReplicationFactor" in body:
        result["min_replication_factor"] = body["minReplicationFactor"]
    if "writeConcern" in body:
        result["write_concern"] = body["writeConcern"]

    # Cluster only
    if "shards" in body:
        result["shards"] = body["shards"]
    if "replicationFactor" in body:
        result["replication_factor"] = body["replicationFactor"]
    if "numberOfShards" in body:
        result["shard_count"] = body["numberOfShards"]
    if "shardKeys" in body:
        result["shard_fields"] = body["shardKeys"]
    if "distributeShardsLike" in body:
        result["shard_like"] = body["distributeShardsLike"]
    if "shardingStrategy" in body:
        result["sharding_strategy"] = body["shardingStrategy"]
    if "smartJoinAttribute" in body:
        result["smart_join_attribute"] = body["smartJoinAttribute"]

    # Key Generator
    if "keyOptions" in body:
        result["key_options"] = format_key_options(body["keyOptions"])

    # Replication only
    if "cid" in body:
        result["cid"] = body["cid"]
    if "version" in body:
        result["version"] = body["version"]
    if "allowUserKeys" in body:
        result["user_keys"] = body["allowUserKeys"]
    if "planId" in body:
        result["plan_id"] = body["planId"]
    if "deleted" in body:
        result["deleted"] = body["deleted"]

    # New in 3.7
    if "syncByRevision" in body:
        result["sync_by_revision"] = body["syncByRevision"]
    if "tempObjectId" in body:
        result["temp_object_id"] = body["tempObjectId"]
    if "usesRevisionsAsDocumentIds" in body:
        result["rev_as_id"] = body["usesRevisionsAsDocumentIds"]
    if "isDisjoint" in body:
        result["disjoint"] = body["isDisjoint"]
    if "isSmartChild" in body:
        result["smart_child"] = body["isSmartChild"]
    if "minRevision" in body:
        result["min_revision"] = body["minRevision"]
    if "schema" in body:
        result["schema"] = body["schema"]
    if body.get("computedValues") is not None:
        result["computedValues"] = body["computedValues"]

    if "internalValidatorType" in body:
        result["internal_validator_type"] = body["internalValidatorType"]

    return verify_format(body, result)


def format_aql_cache(body: Json) -> Json:
    """Format AQL cache data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {
        "mode": body["mode"],
        "max_results": body["maxResults"],
        "max_results_size": body["maxResultsSize"],
        "max_entry_size": body["maxEntrySize"],
        "include_system": body["includeSystem"],
    }
    return verify_format(body, result)


def format_wal_properties(body: Json) -> Json:
    """Format WAL properties.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "allowOversizeEntries" in body:
        result["oversized_ops"] = body["allowOversizeEntries"]
    if "logfileSize" in body:
        result["log_size"] = body["logfileSize"]
    if "historicLogfiles" in body:
        result["historic_logs"] = body["historicLogfiles"]
    if "reserveLogfiles" in body:
        result["reserve_logs"] = body["reserveLogfiles"]
    if "syncInterval" in body:
        result["sync_interval"] = body["syncInterval"]
    if "throttleWait" in body:
        result["throttle_wait"] = body["throttleWait"]
    if "throttleWhenPending" in body:
        result["throttle_limit"] = body["throttleWhenPending"]

    return verify_format(body, result)


def format_wal_transactions(body: Json) -> Json:
    """Format WAL transactions.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "minLastCollected" in body:
        result["last_collected"] = body["minLastCollected"]
    if "minLastSealed" in body:
        result["last_sealed"] = body["minLastSealed"]
    if "runningTransactions" in body:
        result["count"] = body["runningTransactions"]

    return verify_format(body, result)


def format_aql_query(body: Json) -> Json:
    """Format AQL query data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {"id": body["id"], "query": body["query"]}
    if "database" in body:
        result["database"] = body["database"]
    if "bindVars" in body:
        result["bind_vars"] = body["bindVars"]
    if "runTime" in body:
        result["runtime"] = body["runTime"]
    if "started" in body:
        result["started"] = body["started"]
    if "state" in body:
        result["state"] = body["state"]
    if "stream" in body:
        result["stream"] = body["stream"]
    if "user" in body:
        result["user"] = body["user"]

    # New in 3.11
    if "peakMemoryUsage" in body:
        result["peak_memory_usage"] = body["peakMemoryUsage"]
    return verify_format(body, result)


def format_aql_tracking(body: Json) -> Json:
    """Format AQL tracking data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "enabled" in body:
        result["enabled"] = body["enabled"]
    if "maxQueryStringLength" in body:
        result["max_query_string_length"] = body["maxQueryStringLength"]
    if "maxSlowQueries" in body:
        result["max_slow_queries"] = body["maxSlowQueries"]
    if "slowQueryThreshold" in body:
        result["slow_query_threshold"] = body["slowQueryThreshold"]
    if "slowStreamingQueryThreshold" in body:
        result["slow_streaming_query_threshold"] = body["slowStreamingQueryThreshold"]
    if "trackBindVars" in body:
        result["track_bind_vars"] = body["trackBindVars"]
    if "trackSlowQueries" in body:
        result["track_slow_queries"] = body["trackSlowQueries"]

    return verify_format(body, result)


def format_tick_values(body: Json) -> Json:
    """Format tick data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "tickMin" in body:
        result["tick_min"] = body["tickMin"]
    if "tickMax" in body:
        result["tick_max"] = body["tickMax"]
    if "tick" in body:
        result["tick"] = body["tick"]
    if "time" in body:
        result["time"] = body["time"]
    if "server" in body:
        result["server"] = format_server_info(body["server"])

    return verify_format(body, result)


def format_server_info(body: Json) -> Json:
    """Format server data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    return {"version": body["version"], "server_id": body["serverId"]}


def format_server_status(body: Json) -> Json:
    """Format server status.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "agency" in body:
        result["agency"] = body["agency"]
    if "coordinator" in body:
        result["coordinator"] = body["coordinator"]
    if "foxxApi" in body:
        result["foxx_api"] = body["foxxApi"]
    if "host" in body:
        result["host"] = body["host"]
    if "hostname" in body:
        result["hostname"] = body["hostname"]
    if "license" in body:
        result["license"] = body["license"]
    if "mode" in body:
        result["mode"] = body["mode"]
    if "operationMode" in body:
        result["operation_mode"] = body["operationMode"]
    if "pid" in body:
        result["pid"] = body["pid"]
    if "server" in body:
        result["server"] = body["server"]
    if "serverInfo" in body:
        info = body["serverInfo"]
        if "writeOpsEnabled" in info:
            info["write_ops_enabled"] = info.pop("writeOpsEnabled")
        if "readOnly" in info:
            info["read_only"] = info.pop("readOnly")
        result["server_info"] = info
    if "version" in body:
        result["version"] = body["version"]

    return verify_format(body, result)


def format_replication_applier_config(body: Json) -> Json:
    """Format replication applier configuration data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "endpoint" in body:
        result["endpoint"] = body["endpoint"]
    if "database" in body:
        result["database"] = body["database"]
    if "username" in body:
        result["username"] = body["username"]
    if "verbose" in body:
        result["verbose"] = body["verbose"]
    if "incremental" in body:
        result["incremental"] = body["incremental"]
    if "requestTimeout" in body:
        result["request_timeout"] = body["requestTimeout"]
    if "connectTimeout" in body:
        result["connect_timeout"] = body["connectTimeout"]
    if "ignoreErrors" in body:
        result["ignore_errors"] = body["ignoreErrors"]
    if "maxConnectRetries" in body:
        result["max_connect_retries"] = body["maxConnectRetries"]
    if "lockTimeoutRetries" in body:
        result["lock_timeout_retries"] = body["lockTimeoutRetries"]
    if "sslProtocol" in body:
        result["ssl_protocol"] = body["sslProtocol"]
    if "chunkSize" in body:
        result["chunk_size"] = body["chunkSize"]
    if "skipCreateDrop" in body:
        result["skip_create_drop"] = body["skipCreateDrop"]
    if "autoStart" in body:
        result["auto_start"] = body["autoStart"]
    if "adaptivePolling" in body:
        result["adaptive_polling"] = body["adaptivePolling"]
    if "autoResync" in body:
        result["auto_resync"] = body["autoResync"]
    if "autoResyncRetries" in body:
        result["auto_resync_retries"] = body["autoResyncRetries"]
    if "maxPacketSize" in body:
        result["max_packet_size"] = body["maxPacketSize"]
    if "includeSystem" in body:
        result["include_system"] = body["includeSystem"]
    if "includeFoxxQueues" in body:
        result["include_foxx_queues"] = body["includeFoxxQueues"]
    if "requireFromPresent" in body:
        result["require_from_present"] = body["requireFromPresent"]
    if "restrictType" in body:
        result["restrict_type"] = body["restrictType"]
    if "restrictCollections" in body:
        result["restrict_collections"] = body["restrictCollections"]
    if "connectionRetryWaitTime" in body:
        result["connection_retry_wait_time"] = body["connectionRetryWaitTime"]
    if "initialSyncMaxWaitTime" in body:
        result["initial_sync_max_wait_time"] = body["initialSyncMaxWaitTime"]
    if "idleMinWaitTime" in body:
        result["idle_min_wait_time"] = body["idleMinWaitTime"]
    if "idleMaxWaitTime" in body:
        result["idle_max_wait_time"] = body["idleMaxWaitTime"]

    return verify_format(body, result)


def format_applier_progress(body: Json) -> Json:
    """Format replication applier progress data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "time" in body:
        result["time"] = body["time"]
    if "message" in body:
        result["message"] = body["message"]
    if "failedConnects" in body:
        result["failed_connects"] = body["failedConnects"]

    return verify_format(body, result)


def format_applier_error(body: Json) -> Json:
    """Format replication applier error data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "errorNum" in body:
        result["error_num"] = body["errorNum"]
    if "errorMessage" in body:
        result["error_message"] = body["errorMessage"]
    if "time" in body:
        result["time"] = body["time"]

    return verify_format(body, result)


def format_applier_state_details(body: Json) -> Json:
    """Format replication applier state details.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "started" in body:
        result["started"] = body["started"]
    if "running" in body:
        result["running"] = body["running"]
    if "phase" in body:
        result["phase"] = body["phase"]
    if "time" in body:
        result["time"] = body["time"]
    if "safeResumeTick" in body:
        result["safe_resume_tick"] = body["safeResumeTick"]
    if "ticksBehind" in body:
        result["ticks_behind"] = body["ticksBehind"]
    if "lastAppliedContinuousTick" in body:
        result["last_applied_continuous_tick"] = body["lastAppliedContinuousTick"]
    if "lastProcessedContinuousTick" in body:
        result["last_processed_continuous_tick"] = body["lastProcessedContinuousTick"]
    if "lastAvailableContinuousTick" in body:
        result["last_available_continuous_tick"] = body["lastAvailableContinuousTick"]
    if "progress" in body:
        result["progress"] = format_applier_progress(body["progress"])
    if "totalRequests" in body:
        result["total_requests"] = body["totalRequests"]
    if "totalFailedConnects" in body:
        result["total_failed_connects"] = body["totalFailedConnects"]
    if "totalEvents" in body:
        result["total_events"] = body["totalEvents"]
    if "totalDocuments" in body:
        result["total_documents"] = body["totalDocuments"]
    if "totalRemovals" in body:
        result["total_removals"] = body["totalRemovals"]
    if "totalResyncs" in body:
        result["total_resyncs"] = body["totalResyncs"]
    if "totalOperationsExcluded" in body:
        result["total_operations_excluded"] = body["totalOperationsExcluded"]
    if "totalApplyTime" in body:
        result["total_apply_time"] = body["totalApplyTime"]
    if "averageApplyTime" in body:
        result["average_apply_time"] = body["averageApplyTime"]
    if "totalFetchTime" in body:
        result["total_fetch_time"] = body["totalFetchTime"]
    if "averageFetchTime" in body:
        result["average_fetch_time"] = body["averageFetchTime"]
    if "lastError" in body:
        result["last_error"] = format_applier_error(body["lastError"])

    return verify_format(body, result)


def format_replication_applier_state(body: Json) -> Json:
    """Format replication applier state.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "endpoint" in body:
        result["endpoint"] = body["endpoint"]
    if "database" in body:
        result["database"] = body["database"]
    if "username" in body:
        result["username"] = body["username"]
    if "state" in body:
        result["state"] = format_applier_state_details(body["state"])
    if "server" in body:
        result["server"] = format_server_info(body["server"])

    return verify_format(body, result)


def format_replication_state(body: Json) -> Json:
    """Format replication state.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    if not isinstance(body, dict):
        return body

    result: Json = {}
    if "running" in body:
        result["running"] = body["running"]
    if "time" in body:
        result["time"] = body["time"]
    if "lastLogTick" in body:
        result["last_log_tick"] = body["lastLogTick"]
    if "totalEvents" in body:
        result["total_events"] = body["totalEvents"]
    if "lastUncommittedLogTick" in body:
        result["last_uncommitted_log_tick"] = body["lastUncommittedLogTick"]

    return verify_format(body, result)


def format_replication_logger_state(body: Json) -> Json:
    """Format replication collection data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "state" in body:
        result["state"] = format_replication_state(body["state"])
    if "server" in body:
        result["server"] = format_server_info(body["server"])
    if "clients" in body:
        result["clients"] = body["clients"]

    return verify_format(body, result)


def format_replication_collection(body: Json) -> Json:
    """Format replication collection data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "planVersion" in body:
        result["plan_version"] = body["planVersion"]
    if "isReady" in body:
        result["is_ready"] = body["isReady"]
    if "allInSync" in body:
        result["all_in_sync"] = body["allInSync"]
    if "indexes" in body:
        result["indexes"] = [format_index(index) for index in body["indexes"]]
    if "parameters" in body:
        result["parameters"] = format_collection(body["parameters"])

    return verify_format(body, result)


def format_replication_database(body: Json) -> Json:
    """Format replication database data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {
        "id": body["id"],
        "name": body["name"],
        "collections": [
            format_replication_collection(col) for col in body["collections"]
        ],
        "views": [format_view(view) for view in body["views"]],
    }
    if "properties" in body:
        result["properties"] = format_database(body["properties"])

    return verify_format(body, result)


def format_replication_inventory(body: Json) -> Json:
    """Format replication inventory data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "tick" in body:
        result["tick"] = body["tick"]
    if "state" in body:
        result["state"] = format_replication_state(body["state"])

    if "databases" in body:
        result["databases"] = {
            k: format_replication_database(v) for k, v in body["databases"].items()
        }
    if "collections" in body:
        result["collections"] = [
            format_replication_collection(col) for col in body["collections"]
        ]
    if "views" in body:
        result["views"] = [format_view(view) for view in body["views"]]
    if "properties" in body:
        result["properties"] = format_database(body["properties"])

    return verify_format(body, result)


def format_replication_sync(body: Json) -> Json:
    """Format replication sync result.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "collections" in body:
        result["collections"] = body["collections"]
    if "lastLogTick" in body:
        result["last_log_tick"] = body["lastLogTick"]
    return verify_format(body, result)


def format_replication_header(headers: Headers) -> Json:
    """Format replication headers.

    :param headers: Request headers.
    :type headers: dict
    :return: Formatted body.
    :rtype: dict
    """
    headers = {k.lower(): v for k, v in headers.items()}
    result: Json = {}

    if "x-arango-replication-frompresent" in headers:
        result["from_present"] = headers["x-arango-replication-frompresent"] == "true"

    if "x-arango-replication-lastincluded" in headers:
        result["last_included"] = headers["x-arango-replication-lastincluded"]

    if "x-arango-replication-lastscanned" in headers:
        result["last_scanned"] = headers["x-arango-replication-lastscanned"]

    if "x-arango-replication-lasttick" in headers:
        result["last_tick"] = headers["x-arango-replication-lasttick"]

    if "x-arango-replication-active" in headers:
        result["active"] = headers["x-arango-replication-active"] == "true"

    if "x-arango-replication-checkmore" in headers:
        result["check_more"] = headers["x-arango-replication-checkmore"] == "true"

    return result


def format_view_link(body: Json) -> Json:
    """Format view link data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "analyzers" in body:
        result["analyzers"] = body["analyzers"]
    if "fields" in body:
        result["fields"] = body["fields"]
    if "includeAllFields" in body:
        result["include_all_fields"] = body["includeAllFields"]
    if "trackListPositions" in body:
        result["track_list_positions"] = body["trackListPositions"]
    if "storeValues" in body:
        result["store_values"] = body["storeValues"]
    if "primaryKeyCache" in body:
        result["primaryKeyCache"] = body["primaryKeyCache"]
    if "companies" in body:
        result["companies"] = body["companies"]

    return verify_format(body, result)


def format_view_index(body: Json) -> Json:
    """Format view index data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "collection" in body:
        result["collection"] = body["collection"]
    if "index" in body:
        result["index"] = body["index"]

    return verify_format(body, result)


def format_view_consolidation_policy(body: Json) -> Json:
    """Format view consolidation policy data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "type" in body:
        result["type"] = body["type"]
    if "threshold" in body:
        result["threshold"] = body["threshold"]
    if "segmentsMin" in body:
        result["segments_min"] = body["segmentsMin"]
    if "segmentsMax" in body:
        result["segments_max"] = body["segmentsMax"]
    if "segmentsBytesMax" in body:
        result["segments_bytes_max"] = body["segmentsBytesMax"]
    if "segmentsBytesFloor" in body:
        result["segments_bytes_floor"] = body["segmentsBytesFloor"]
    if "minScore" in body:
        result["min_score"] = body["minScore"]

    return verify_format(body, result)


def format_view(body: Json) -> Json:
    """Format view data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "globallyUniqueId" in body:
        result["global_id"] = body["globallyUniqueId"]
    if "id" in body:
        result["id"] = body["id"]
    if "name" in body:
        result["name"] = body["name"]
    if "type" in body:
        result["type"] = body["type"]
    if "cleanupIntervalStep" in body:
        result["cleanup_interval_step"] = body["cleanupIntervalStep"]
    if "commitIntervalMsec" in body:
        result["commit_interval_msec"] = body["commitIntervalMsec"]
    if "consolidationIntervalMsec" in body:
        result["consolidation_interval_msec"] = body["consolidationIntervalMsec"]
    if "consolidationPolicy" in body:
        result["consolidation_policy"] = format_view_consolidation_policy(
            body["consolidationPolicy"]
        )
    if "primarySort" in body:
        result["primary_sort"] = body["primarySort"]
    if "primarySortCompression" in body:
        result["primary_sort_compression"] = body["primarySortCompression"]
    if "storedValues" in body:
        result["stored_values"] = body["storedValues"]
    if "writebufferIdle" in body:
        result["writebuffer_idle"] = body["writebufferIdle"]
    if "writebufferActive" in body:
        result["writebuffer_active"] = body["writebufferActive"]
    if "writebufferSizeMax" in body:
        result["writebuffer_max_size"] = body["writebufferSizeMax"]
    if "links" in body:
        result["links"] = body["links"]
    if "indexes" in body:
        result["indexes"] = body["indexes"]

    # Introduced in 3.9.6 EE
    if "primaryKeyCache" in body:
        result["primaryKeyCache"] = body["primaryKeyCache"]
    if "primarySortCache" in body:
        result["primarySortCache"] = body["primarySortCache"]

    # Introduced in 3.12 EE
    if "optimizeTopK" in body:
        result["optimizeTopK"] = body["optimizeTopK"]

    return verify_format(body, result)


def format_vertex(body: Json) -> Json:
    """Format vertex data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    vertex: Json = body["vertex"]
    if "_oldRev" in vertex:
        vertex["_old_rev"] = vertex.pop("_oldRev")

    if "new" in body or "old" in body:
        result: Json = {"vertex": vertex}
        if "new" in body:
            result["new"] = body["new"]
        if "old" in body:
            result["old"] = body["old"]
        return result
    else:
        return vertex


def format_edge(body: Json) -> Json:
    """Format edge data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    edge: Json = body["edge"]
    if "_oldRev" in edge:
        edge["_old_rev"] = edge.pop("_oldRev")

    if "new" in body or "old" in body:
        result: Json = {"edge": edge}
        if "new" in body:
            result["new"] = body["new"]
        if "old" in body:
            result["old"] = body["old"]
        return result
    else:
        return edge


def format_tls(body: Json) -> Json:
    """Format TLS data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = body
    return verify_format(body, result)


def format_backup(body: Json) -> Json:
    """Format backup entry.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "previous" in body:
        result["previous"] = body["previous"]
    if "id" in body:
        result["backup_id"] = body["id"]
    if "datetime" in body:
        result["datetime"] = body["datetime"]
    if "potentiallyInconsistent" in body:
        result["potentially_inconsistent"] = body["potentiallyInconsistent"]
    if "sizeInBytes" in body:
        result["size_in_bytes"] = body["sizeInBytes"]
    if "nrDBServers" in body:
        result["dbserver_count"] = body["nrDBServers"]
    if "nrFiles" in body:
        result["file_count"] = body["nrFiles"]

    if "available" in body:
        result["available"] = body["available"]
    if "version" in body:
        result["version"] = body["version"]
    if "keys" in body:
        result["keys"] = body["keys"]
    if "nrPiecesPresent" in body:
        result["pieces_present"] = body["nrPiecesPresent"]

    if "countIncludesFilesOnly" in body:
        result["count_includes_files_only"] = body["countIncludesFilesOnly"]

    return verify_format(body, result)


def format_backups(body: Json) -> Json:
    """Format backup entries.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "server" in body:
        result["server"] = body["server"]
    if "list" in body:
        result["list"] = {
            key: format_backup(backup) for key, backup in body["list"].items()
        }
    return verify_format(body, result)


def format_backup_restore(body: Json) -> Json:
    """Format backup restore data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "id" in body:
        result["backup_id"] = body["id"]
    if "isCluster" in body:
        result["is_cluster"] = body["isCluster"]
    if "previous" in body:
        result["previous"] = body["previous"]

    return verify_format(body, result)


def format_backup_dbserver(body: Json) -> Json:
    """Format backup DBserver data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    return {"status": body["Status"]}


def format_backup_transfer(body: Json) -> Json:
    """Format backup download/upload data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}
    if "Timestamp" in body:
        result["timestamp"] = body["Timestamp"]
    if "DownloadId" in body:
        result["download_id"] = body["DownloadId"]
    if "downloadId" in body:
        result["download_id"] = body["downloadId"]
    if "UploadId" in body:
        result["upload_id"] = body["UploadId"]
    if "uploadId" in body:
        result["upload_id"] = body["uploadId"]
    if "Cancelled" in body:
        result["cancelled"] = body["Cancelled"]
    if "BackupId" in body:
        result["backup_id"] = body["BackupId"]
    if "DBServers" in body:
        result["dbservers"] = {
            k: format_backup_dbserver(v) for k, v in body["DBServers"].items()
        }
    return verify_format(body, result)


def format_service_data(body: Json) -> Json:
    """Format Foxx service data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    if "manifest" in body:
        manifest = body["manifest"]
        if "defaultDocument" in manifest:
            manifest["default_document"] = manifest.pop("defaultDocument")

    return body


def format_pregel_job_data(body: Json) -> Json:
    """Format Pregel job data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {}

    if "id" in body:
        result["id"] = body["id"]
    if "algorithm" in body:
        result["algorithm"] = body["algorithm"]
    if "created" in body:
        result["created"] = body["created"]
    if "expires" in body:
        result["expires"] = body["expires"]
    if "ttl" in body:
        result["ttl"] = body["ttl"]
    if "algorithm" in body:
        result["algorithm"] = body["algorithm"]
    if "state" in body:
        result["state"] = body["state"]
    if "gss" in body:
        result["gss"] = body["gss"]
    if "totalRuntime" in body:
        result["total_runtime"] = body["totalRuntime"]
    if "startupTime" in body:
        result["startup_time"] = body["startupTime"]
    if "computationTime" in body:
        result["computation_time"] = body["computationTime"]
    if "storageTime" in body:
        result["storageTime"] = body["storageTime"]
    if "gssTimes" in body:
        result["gssTimes"] = body["gssTimes"]
    if "reports" in body:
        result["reports"] = body["reports"]
    if "vertexCount" in body:
        result["vertex_count"] = body["vertexCount"]
    if "edgeCount" in body:
        result["edge_count"] = body["edgeCount"]
    if "aggregators" in body:
        result["aggregators"] = body["aggregators"]
    if "receivedCount" in body:
        result["received_count"] = body["receivedCount"]
    if "sendCount" in body:
        result["send_count"] = body["sendCount"]

    # The detail element was introduced in 3.10
    if "detail" in body:
        result["detail"] = body["detail"]
    if "database" in body:
        result["database"] = body["database"]
    if "masterContext" in body:
        result["master_context"] = body["masterContext"]
    if "parallelism" in body:
        result["parallelism"] = body["parallelism"]
    if "useMemoryMaps" in body:
        result["use_memory_maps"] = body["useMemoryMaps"]

    # Introduced in 3.11
    if "user" in body:
        result["user"] = body["user"]
    if "graphLoaded" in body:
        result["graph_loaded"] = body["graphLoaded"]

    return verify_format(body, result)


def format_pregel_job_list(body: Sequence[Json]) -> Json:
    """Format Pregel job list data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result: Json = {"jobs": [format_pregel_job_data(j) for j in body]}

    return verify_format(body, result)


def format_graph_properties(body: Json) -> Json:
    """Format graph properties.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {
        "id": body["_id"],
        "key": body["_key"],
        "name": body["name"],
        "revision": body["_rev"],
        "orphan_collections": body["orphanCollections"],
        "edge_definitions": [
            {
                "edge_collection": edge_definition["collection"],
                "from_vertex_collections": edge_definition["from"],
                "to_vertex_collections": edge_definition["to"],
            }
            for edge_definition in body["edgeDefinitions"]
        ],
    }
    if "isSmart" in body:
        result["smart"] = body["isSmart"]
    if "isSatellite" in body:
        result["is_satellite"] = body["isSatellite"]
    if "smartGraphAttribute" in body:
        result["smart_field"] = body["smartGraphAttribute"]
    if "numberOfShards" in body:
        result["shard_count"] = body["numberOfShards"]
    if "replicationFactor" in body:
        result["replication_factor"] = body["replicationFactor"]
    if "minReplicationFactor" in body:
        result["min_replication_factor"] = body["minReplicationFactor"]
    if "writeConcern" in body:
        result["write_concern"] = body["writeConcern"]

    return verify_format(body, result)


def format_query_cache_entry(body: Json) -> Json:
    """Format AQL query cache entry.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}

    if "hash" in body:
        result["hash"] = body["hash"]
    if "query" in body:
        result["query"] = body["query"]
    if "bindVars" in body:
        result["bind_vars"] = body["bindVars"]
    if "size" in body:
        result["size"] = body["size"]
    if "results" in body:
        result["results"] = body["results"]
    if "started" in body:
        result["started"] = body["started"]
    if "hits" in body:
        result["hits"] = body["hits"]
    if "runTime" in body:
        result["runtime"] = body["runTime"]
    if "dataSources" in body:
        result["data_sources"] = body["dataSources"]

    return verify_format(body, result)


def format_query_rule_item(body: Json) -> Json:
    """Format AQL query rule item.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}

    if "name" in body:
        result["name"] = body["name"]
    if "flags" in body:
        result["flags"] = format_query_rule_item_flags(body["flags"])

    return verify_format(body, result)


def format_query_rule_item_flags(body: Json) -> Json:
    """Format AQL query rule item flags.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}

    if "hidden" in body:
        result["hidden"] = body["hidden"]
    if "clusterOnly" in body:
        result["clusterOnly"] = body["clusterOnly"]
    if "canBeDisabled" in body:
        result["canBeDisabled"] = body["canBeDisabled"]
    if "canCreateAdditionalPlans" in body:
        result["canCreateAdditionalPlans"] = body["canCreateAdditionalPlans"]
    if "disabledByDefault" in body:
        result["disabledByDefault"] = body["disabledByDefault"]
    if "enterpriseOnly" in body:
        result["enterpriseOnly"] = body["enterpriseOnly"]

    return verify_format(body, result)
