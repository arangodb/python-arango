def verify_format(_, res):
    return res


def format_index(body):  # pragma: no cover
    """Format index data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {
        'id': body['id'].split('/', 1)[-1],
        'fields': body['fields']
    }
    if 'type' in body:
        result['type'] = body['type']
    if 'name' in body:
        result['name'] = body['name']
    if 'deduplicate' in body:
        result['deduplicate'] = body['deduplicate']
    if 'sparse' in body:
        result['sparse'] = body['sparse']
    if 'unique' in body:
        result['unique'] = body['unique']
    if 'minLength' in body:
        result['min_length'] = body['minLength']
    if 'geoJson' in body:
        result['geo_json'] = body['geoJson']
    if 'ignoreNull' in body:
        result['ignore_none'] = body['ignoreNull']
    if 'selectivityEstimate' in body:
        result['selectivity'] = body['selectivityEstimate']
    if 'isNewlyCreated' in body:
        result['new'] = body['isNewlyCreated']
    if 'expireAfter' in body:
        result['expiry_time'] = body['expireAfter']
    if 'inBackground' in body:
        result['in_background'] = body['inBackground']
    if 'bestIndexedLevel' in body:
        result['best_indexed_level'] = body['bestIndexedLevel']
    if 'worstIndexedLevel' in body:
        result['worst_indexed_level'] = body['worstIndexedLevel']
    if 'maxNumCoverCells' in body:
        result['max_num_cover_cells'] = body['maxNumCoverCells']

    return verify_format(body, result)


def format_key_options(body):  # pragma: no cover
    """Format collection key options data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}

    if 'type' in body:
        result['key_generator'] = body['type']
    if 'increment' in body:
        result['key_increment'] = body['increment']
    if 'offset' in body:
        result['key_offset'] = body['offset']
    if 'allowUserKeys' in body:
        result['user_keys'] = body['allowUserKeys']
    if 'lastValue' in body:
        result['key_last_value'] = body['lastValue']

    return verify_format(body, result)


def format_database(body):  # pragma: no cover
    """Format databases info.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}

    if 'id' in body:
        result['id'] = body['id']
    if 'name' in body:
        result['name'] = body['name']
    if 'path' in body:
        result['path'] = body['path']
    if 'system' in body:
        result['system'] = body['system']
    if 'isSystem' in body:
        result['system'] = body['isSystem']

    # Cluster only
    if 'sharding' in body:
        result['sharding'] = body['sharding']
    if 'replicationFactor' in body:
        result['replication_factor'] = body['replicationFactor']
    if 'writeConcern' in body:
        result['write_concern'] = body['writeConcern']

    return verify_format(body, result)


def format_collection(body):  # pragma: no cover
    """Format collection data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}

    if 'id' in body:
        result['id'] = body['id']
    if 'objectId' in body:
        result['object_id'] = body['objectId']
    if 'name' in body:
        result['name'] = body['name']
    if 'isSystem' in body:
        result['system'] = body['isSystem']
    if 'isSmart' in body:
        result['smart'] = body['isSmart']
    if 'type' in body:
        result['type'] = body['type']
        result['edge'] = body['type'] == 3
    if 'waitForSync' in body:
        result['sync'] = body['waitForSync']

    if 'status' in body:
        result['status'] = body['status']
    if 'statusString' in body:
        result['status_string'] = body['statusString']
    if 'globallyUniqueId' in body:
        result['global_id'] = body['globallyUniqueId']
    if 'cacheEnabled' in body:
        result['cache'] = body['cacheEnabled']
    if 'replicationFactor' in body:
        result['replication_factor'] = body['replicationFactor']
    if 'minReplicationFactor' in body:
        result['min_replication_factor'] = body['minReplicationFactor']
    if 'writeConcern' in body:
        result['write_concern'] = body['writeConcern']

    # MMFiles only
    if 'doCompact' in body:
        result['compact'] = body['doCompact']
    if 'journalSize' in body:
        result['journal_size'] = body['journalSize']
    if 'isVolatile' in body:
        result['volatile'] = body['isVolatile']
    if 'indexBuckets' in body:
        result['index_bucket_count'] = body['indexBuckets']

    # Cluster only
    if 'shards' in body:
        result['shards'] = body['shards']
    if 'replicationFactor' in body:
        result['replication_factor'] = body['replicationFactor']
    if 'numberOfShards' in body:
        result['shard_count'] = body['numberOfShards']
    if 'shardKeys' in body:
        result['shard_fields'] = body['shardKeys']
    if 'distributeShardsLike' in body:
        result['shard_like'] = body['distributeShardsLike']
    if 'shardingStrategy' in body:
        result['sharding_strategy'] = body['shardingStrategy']
    if 'smartJoinAttribute' in body:
        result['smart_join_attribute'] = body['smartJoinAttribute']

    # Key Generator
    if 'keyOptions' in body:
        result['key_options'] = format_key_options(body['keyOptions'])

    # Replication only
    if 'cid' in body:
        result['cid'] = body['cid']
    if 'version' in body:
        result['version'] = body['version']
    if 'allowUserKeys' in body:
        result['user_keys'] = body['allowUserKeys']
    if 'planId' in body:
        result['plan_id'] = body['planId']
    if 'deleted' in body:
        result['deleted'] = body['deleted']

    # New in 3.7
    if 'syncByRevision' in body:
        result['sync_by_revision'] = body['syncByRevision']
    if 'tempObjectId' in body:
        result['temp_object_id'] = body['tempObjectId']
    if 'usesRevisionsAsDocumentIds' in body:
        result['rev_as_id'] = body['usesRevisionsAsDocumentIds']
    if 'isDisjoint' in body:
        result['disjoint'] = body['isDisjoint']
    if 'isSmartChild' in body:
        result['smart_child'] = body['isSmartChild']
    if 'minRevision' in body:
        result['min_revision'] = body['minRevision']
    if 'schema' in body:
        result['schema'] = body['schema']

    return verify_format(body, result)


def format_aql_cache(body):
    """Format AQL cache data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {
        'mode': body['mode'],
        'max_results': body['maxResults'],
        'max_results_size': body['maxResultsSize'],
        'max_entry_size': body['maxEntrySize'],
        'include_system': body['includeSystem']
    }
    return verify_format(body, result)


def format_wal_properties(body):  # pragma: no cover
    """Format WAL properties.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'allowOversizeEntries' in body:
        result['oversized_ops'] = body['allowOversizeEntries']
    if 'logfileSize' in body:
        result['log_size'] = body['logfileSize']
    if 'historicLogfiles' in body:
        result['historic_logs'] = body['historicLogfiles']
    if 'reserveLogfiles' in body:
        result['reserve_logs'] = body['reserveLogfiles']
    if 'syncInterval' in body:
        result['sync_interval'] = body['syncInterval']
    if 'throttleWait' in body:
        result['throttle_wait'] = body['throttleWait']
    if 'throttleWhenPending' in body:
        result['throttle_limit'] = body['throttleWhenPending']

    return verify_format(body, result)


def format_wal_transactions(body):  # pragma: no cover
    """Format WAL transactions.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'minLastCollected' in body:
        result['last_collected'] = body['minLastCollected']
    if 'minLastSealed' in body:
        result['last_sealed'] = body['minLastSealed']
    if 'runningTransactions' in body:
        result['count'] = body['runningTransactions']

    return verify_format(body, result)


def format_aql_query(body):  # pragma: no cover
    """Format AQL query data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {'id': body['id'], 'query': body['query']}
    if 'started' in body:
        result['started'] = body['started']
    if 'state' in body:
        result['state'] = body['state']
    if 'stream' in body:
        result['stream'] = body['stream']
    if 'bindVars' in body:
        result['bind_vars'] = body['bindVars']
    if 'runTime' in body:
        result['runtime'] = body['runTime']

    return verify_format(body, result)


def format_aql_tracking(body):  # pragma: no cover
    """Format AQL tracking data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'enabled' in body:
        result['enabled'] = body['enabled']
    if 'maxQueryStringLength' in body:
        result['max_query_string_length'] = body['maxQueryStringLength']
    if 'maxSlowQueries' in body:
        result['max_slow_queries'] = body['maxSlowQueries']
    if 'slowQueryThreshold' in body:
        result['slow_query_threshold'] = body['slowQueryThreshold']
    if 'slowStreamingQueryThreshold' in body:
        result['slow_streaming_query_threshold'] = \
            body['slowStreamingQueryThreshold']
    if 'trackBindVars' in body:
        result['track_bind_vars'] = body['trackBindVars']
    if 'trackSlowQueries' in body:
        result['track_slow_queries'] = body['trackSlowQueries']

    return verify_format(body, result)


def format_tick_values(body):  # pragma: no cover
    """Format tick data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}

    if 'tickMin' in body:
        result['tick_min'] = body['tickMin']
    if 'tickMax' in body:
        result['tick_max'] = body['tickMax']
    if 'tick' in body:
        result['tick'] = body['tick']
    if 'time' in body:
        result['time'] = body['time']
    if 'server' in body:
        result['server'] = format_server_info(body['server'])

    return verify_format(body, result)


def format_server_info(body):  # pragma: no cover
    """Format server data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    return {'version': body['version'], 'server_id': body['serverId']}


def format_replication_applier_config(body):  # pragma: no cover
    """Format replication applier configuration data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'endpoint' in body:
        result['endpoint'] = body['endpoint']
    if 'database' in body:
        result['database'] = body['database']
    if 'username' in body:
        result['username'] = body['username']
    if 'verbose' in body:
        result['verbose'] = body['verbose']
    if 'incremental' in body:
        result['incremental'] = body['incremental']
    if 'requestTimeout' in body:
        result['request_timeout'] = body['requestTimeout']
    if 'connectTimeout' in body:
        result['connect_timeout'] = body['connectTimeout']
    if 'ignoreErrors' in body:
        result['ignore_errors'] = body['ignoreErrors']
    if 'maxConnectRetries' in body:
        result['max_connect_retries'] = body['maxConnectRetries']
    if 'lockTimeoutRetries' in body:
        result['lock_timeout_retries'] = body['lockTimeoutRetries']
    if 'sslProtocol' in body:
        result['ssl_protocol'] = body['sslProtocol']
    if 'chunkSize' in body:
        result['chunk_size'] = body['chunkSize']
    if 'skipCreateDrop' in body:
        result['skip_create_drop'] = body['skipCreateDrop']
    if 'autoStart' in body:
        result['auto_start'] = body['autoStart']
    if 'adaptivePolling' in body:
        result['adaptive_polling'] = body['adaptivePolling']
    if 'autoResync' in body:
        result['auto_resync'] = body['autoResync']
    if 'autoResyncRetries' in body:
        result['auto_resync_retries'] = body['autoResyncRetries']
    if 'maxPacketSize' in body:
        result['max_packet_size'] = body['maxPacketSize']
    if 'includeSystem' in body:
        result['include_system'] = body['includeSystem']
    if 'includeFoxxQueues' in body:
        result['include_foxx_queues'] = body['includeFoxxQueues']
    if 'requireFromPresent' in body:
        result['require_from_present'] = body['requireFromPresent']
    if 'restrictType' in body:
        result['restrict_type'] = body['restrictType']
    if 'restrictCollections' in body:
        result['restrict_collections'] = body['restrictCollections']
    if 'connectionRetryWaitTime' in body:
        result['connection_retry_wait_time'] = body['connectionRetryWaitTime']
    if 'initialSyncMaxWaitTime' in body:
        result['initial_sync_max_wait_time'] = body['initialSyncMaxWaitTime']
    if 'idleMinWaitTime' in body:
        result['idle_min_wait_time'] = body['idleMinWaitTime']
    if 'idleMaxWaitTime' in body:
        result['idle_max_wait_time'] = body['idleMaxWaitTime']

    return verify_format(body, result)


def format_applier_progress(body):  # pragma: no cover
    """Format replication applier progress data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'time' in body:
        result['time'] = body['time']
    if 'message' in body:
        result['message'] = body['message']
    if 'failedConnects' in body:
        result['failed_connects'] = body['failedConnects']

    return verify_format(body, result)


def format_applier_error(body):  # pragma: no cover
    """Format replication applier error data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'errorNum' in body:
        result['error_num'] = body['errorNum']
    if 'errorMessage' in body:
        result['error_message'] = body['errorMessage']
    if 'time' in body:
        result['time'] = body['time']

    return verify_format(body, result)


def format_applier_state_details(body):  # pragma: no cover
    """Format replication applier state details.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'started' in body:
        result['started'] = body['started']
    if 'running' in body:
        result['running'] = body['running']
    if 'phase' in body:
        result['phase'] = body['phase']
    if 'time' in body:
        result['time'] = body['time']
    if 'safeResumeTick' in body:
        result['safe_resume_tick'] = body['safeResumeTick']
    if 'ticksBehind' in body:
        result['ticks_behind'] = body['ticksBehind']
    if 'lastAppliedContinuousTick' in body:
        result['last_applied_continuous_tick'] = \
            body['lastAppliedContinuousTick']
    if 'lastProcessedContinuousTick' in body:
        result['last_processed_continuous_tick'] = \
            body['lastProcessedContinuousTick']
    if 'lastAvailableContinuousTick' in body:
        result['last_available_continuous_tick'] = \
            body['lastAvailableContinuousTick']
    if 'progress' in body:
        result['progress'] = format_applier_progress(body['progress'])
    if 'totalRequests' in body:
        result['total_requests'] = body['totalRequests']
    if 'totalFailedConnects' in body:
        result['total_failed_connects'] = body['totalFailedConnects']
    if 'totalEvents' in body:
        result['total_events'] = body['totalEvents']
    if 'totalDocuments' in body:
        result['total_documents'] = body['totalDocuments']
    if 'totalRemovals' in body:
        result['total_removals'] = body['totalRemovals']
    if 'totalResyncs' in body:
        result['total_resyncs'] = body['totalResyncs']
    if 'totalOperationsExcluded' in body:
        result['total_operations_excluded'] = body['totalOperationsExcluded']
    if 'totalApplyTime' in body:
        result['total_apply_time'] = body['totalApplyTime']
    if 'averageApplyTime' in body:
        result['average_apply_time'] = body['averageApplyTime']
    if 'totalFetchTime' in body:
        result['total_fetch_time'] = body['totalFetchTime']
    if 'averageFetchTime' in body:
        result['average_fetch_time'] = body['averageFetchTime']
    if 'lastError' in body:
        result['last_error'] = format_applier_error(body['lastError'])

    return verify_format(body, result)


def format_replication_applier_state(body):  # pragma: no cover
    """Format replication applier state.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'endpoint' in body:
        result['endpoint'] = body['endpoint']
    if 'database' in body:
        result['database'] = body['database']
    if 'username' in body:
        result['username'] = body['username']
    if 'state' in body:
        result['state'] = format_applier_state_details(body['state'])
    if 'server' in body:
        result['server'] = format_server_info(body['server'])

    return verify_format(body, result)


def format_replication_state(body):  # pragma: no cover
    """Format replication state.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    if not isinstance(body, dict):
        return body

    result = {}
    if 'running' in body:
        result['running'] = body['running']
    if 'time' in body:
        result['time'] = body['time']
    if 'lastLogTick' in body:
        result['last_log_tick'] = body['lastLogTick']
    if 'totalEvents' in body:
        result['total_events'] = body['totalEvents']
    if 'lastUncommittedLogTick' in body:
        result['last_uncommitted_log_tick'] = body['lastUncommittedLogTick']

    return verify_format(body, result)


def format_replication_logger_state(body):  # pragma: no cover
    """Format replication collection data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'state' in body:
        result['state'] = format_replication_state(body['state'])
    if 'server' in body:
        result['server'] = format_server_info(body['server'])
    if 'clients' in body:
        result['clients'] = body['clients']

    return verify_format(body, result)


def format_replication_collection(body):  # pragma: no cover
    """Format replication collection data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'planVersion' in body:
        result['plan_version'] = body['planVersion']
    if 'isReady' in body:
        result['is_ready'] = body['isReady']
    if 'allInSync' in body:
        result['all_in_sync'] = body['allInSync']
    if 'indexes' in body:
        result['indexes'] = [format_index(index) for index in body['indexes']]
    if 'parameters' in body:
        result['parameters'] = format_collection(body['parameters'])

    return verify_format(body, result)


def format_replication_database(body):  # pragma: no cover
    """Format replication database data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {
        'id': body['id'],
        'name': body['name'],
        'collections': [
            format_replication_collection(col)
            for col in body['collections']
        ],
        'views': [format_view(view) for view in body['views']]
    }
    if 'properties' in body:
        result['properties'] = format_database(body['properties'])

    return verify_format(body, result)


def format_replication_inventory(body):  # pragma: no cover
    """Format replication inventory data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'tick' in body:
        result['tick'] = body['tick']
    if 'state' in body:
        result['state'] = format_replication_state(body['state'])

    if 'databases' in body:
        result['databases'] = {
            k: format_replication_database(v)
            for k, v in body['databases'].items()
        }
    if 'collections' in body:
        result['collections'] = [
            format_replication_collection(col)
            for col in body['collections']
        ]
    if 'views' in body:
        result['views'] = [format_view(view) for view in body['views']]
    if 'properties' in body:
        result['properties'] = format_database(body['properties'])

    return verify_format(body, result)


def format_replication_sync(body):  # pragma: no cover
    """Format replication sync result.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'collections' in body:
        result['collections'] = body['collections']
    if 'lastLogTick' in body:
        result['last_log_tick'] = body['lastLogTick']
    return verify_format(body, result)


def format_replication_header(headers):  # pragma: no cover
    """Format replication headers.

    :param headers: Request headers.
    :type headers: dict
    :return: Formatted body.
    :rtype: dict
    """
    headers = {k.lower(): v for k, v in headers.items()}
    result = {}

    if 'x-arango-replication-frompresent' in headers:
        result['from_present'] = \
            headers['x-arango-replication-frompresent'] == 'true'

    if 'x-arango-replication-lastincluded' in headers:
        result['last_included'] = \
            headers['x-arango-replication-lastincluded']

    if 'x-arango-replication-lastscanned' in headers:
        result['last_scanned'] = \
            headers['x-arango-replication-lastscanned']

    if 'x-arango-replication-lasttick' in headers:
        result['last_tick'] = \
            headers['x-arango-replication-lasttick']

    if 'x-arango-replication-active' in headers:
        result['active'] = \
            headers['x-arango-replication-active'] == 'true'

    if 'x-arango-replication-checkmore' in headers:
        result['check_more'] = \
            headers['x-arango-replication-checkmore'] == 'true'

    return result


def format_view_link(body):  # pragma: no cover
    """Format view link data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'analyzers' in body:
        result['analyzers'] = body['analyzers']
    if 'fields' in body:
        result['fields'] = body['fields']
    if 'includeAllFields' in body:
        result['include_all_fields'] = body['includeAllFields']
    if 'trackListPositions' in body:
        result['track_list_positions'] = body['trackListPositions']
    if 'storeValues' in body:
        result['store_values'] = body['storeValues']

    return verify_format(body, result)


def format_view_consolidation_policy(body):  # pragma: no cover
    """Format view consolidation policy data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'type' in body:
        result['type'] = body['type']
    if 'threshold' in body:
        result['threshold'] = body['threshold']
    if 'segmentsMin' in body:
        result['segments_min'] = body['segmentsMin']
    if 'segmentsMax' in body:
        result['segments_max'] = body['segmentsMax']
    if 'segmentsBytesMax' in body:
        result['segments_bytes_max'] = body['segmentsBytesMax']
    if 'segmentsBytesFloor' in body:
        result['segments_bytes_floor'] = body['segmentsBytesFloor']
    if 'minScore' in body:
        result['min_score'] = body['minScore']

    return verify_format(body, result)


def format_view(body):  # pragma: no cover
    """Format view data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = {}
    if 'globallyUniqueId' in body:
        result['global_id'] = body['globallyUniqueId']
    if 'id' in body:
        result['id'] = body['id']
    if 'name' in body:
        result['name'] = body['name']
    if 'type' in body:
        result['type'] = body['type']
    if 'cleanupIntervalStep' in body:
        result['cleanup_interval_step'] = body['cleanupIntervalStep']
    if 'commitIntervalMsec' in body:
        result['commit_interval_msec'] = body['commitIntervalMsec']
    if 'consolidationIntervalMsec' in body:
        result['consolidation_interval_msec'] = \
            body['consolidationIntervalMsec']
    if 'consolidationPolicy' in body:
        result['consolidation_policy'] = \
            format_view_consolidation_policy(body['consolidationPolicy'])
    if 'primarySort' in body:
        result['primary_sort'] = body['primarySort']
    if 'primarySortCompression' in body:
        result['primary_sort_compression'] = body['primarySortCompression']
    if 'storedValues' in body:
        result['stored_values'] = body['storedValues']
    if 'writebufferIdle' in body:
        result['writebuffer_idle'] = body['writebufferIdle']
    if 'writebufferActive' in body:
        result['writebuffer_active'] = body['writebufferActive']
    if 'writebufferSizeMax' in body:
        result['writebuffer_max_size'] = body['writebufferSizeMax']
    if 'links' in body:
        result['links'] = [format_view_link(link) for link in body['links']]

    return verify_format(body, result)


def format_vertex(body):  # pragma: no cover
    """Format vertex data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    vertex = body['vertex']
    if '_oldRev' in vertex:
        vertex['_old_rev'] = vertex.pop('_oldRev')

    if 'new' in body or 'old' in body:
        result = {'vertex': vertex}
        if 'new' in body:
            result['new'] = body['new']
        if 'old' in body:
            result['old'] = body['old']
        return result
    else:
        return vertex


def format_edge(body):  # pragma: no cover
    """Format edge data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    edge = body['edge']
    if '_oldRev' in edge:
        edge['_old_rev'] = edge.pop('_oldRev')

    if 'new' in body or 'old' in body:
        result = {'edge': edge}
        if 'new' in body:
            result['new'] = body['new']
        if 'old' in body:
            result['old'] = body['old']
        return result
    else:
        return edge


def format_tls(body):  # pragma: no cover
    """Format TLS data.

    :param body: Input body.
    :type body: dict
    :return: Formatted body.
    :rtype: dict
    """
    result = body
    return verify_format(body, result)
