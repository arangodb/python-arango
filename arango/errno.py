##################
# General errors #
##################

# no error
NO_ERROR = 0

# failed
FAILED = 1

# system error
SYS_ERROR = 2

# out of memory
OUT_OF_MEMORY = 3

# internal error
INTERNAL = 4

# illegal number
ILLEGAL_NUMBER = 5

# numeric overflow
NUMERIC_OVERFLOW = 6

# illegal option
ILLEGAL_OPTION = 7

# dead process identifier
DEAD_PID = 8

# not implemented
NOT_IMPLEMENTED = 9

# bad parameter
BAD_PARAMETER = 10

# forbidden
FORBIDDEN = 11

# csv is corrupt
CORRUPTED_CSV = 13

# file not found
FILE_NOT_FOUND = 14

# cannot write file
CANNOT_WRITE_FILE = 15

# cannot overwrite file
CANNOT_OVERWRITE_FILE = 16

# type error
TYPE_ERROR = 17

# lock timeout
LOCK_TIMEOUT = 18

# cannot create directory
CANNOT_CREATE_DIRECTORY = 19

# cannot create temporary file
CANNOT_CREATE_TEMP_FILE = 20

# canceled request
REQUEST_CANCELED = 21

# intentional debug error
DEBUG = 22

# IP address is invalid
IP_ADDRESS_INVALID = 25

# file exists
FILE_EXISTS = 27

# locked
LOCKED = 28

# deadlock detected
DEADLOCK = 29

# shutdown in progress
SHUTTING_DOWN = 30

# only enterprise version
ONLY_ENTERPRISE = 31

# resource limit exceeded
RESOURCE_LIMIT = 32

# icu error: %s
ICU_ERROR = 33

# cannot read file
CANNOT_READ_FILE = 34

# incompatible server version
INCOMPATIBLE_VERSION = 35

# disabled
DISABLED = 36

# malformed json
MALFORMED_JSON = 37

# startup ongoing
STARTING_UP = 38

# error during deserialization
DESERIALIZE = 39

# reached end of file
END_OF_FILE = 40

###########################
# HTTP error status codes #
###########################

# bad parameter
HTTP_BAD_PARAMETER = 400

# unauthorized
HTTP_UNAUTHORIZED = 401

# forbidden
HTTP_FORBIDDEN = 403

# not found
HTTP_NOT_FOUND = 404

# method not supported
HTTP_METHOD_NOT_ALLOWED = 405

# request not acceptable
HTTP_NOT_ACCEPTABLE = 406

# request timeout
HTTP_REQUEST_TIMEOUT = 408

# conflict
HTTP_CONFLICT = 409

# content permanently deleted
HTTP_GONE = 410

# precondition failed
HTTP_PRECONDITION_FAILED = 412

# enhance your calm
HTTP_ENHANCE_YOUR_CALM = 420

# internal server error
HTTP_SERVER_ERROR = 500

# not implemented
HTTP_NOT_IMPLEMENTED = 501

# service unavailable
HTTP_SERVICE_UNAVAILABLE = 503

# gateway timeout
HTTP_GATEWAY_TIMEOUT = 504

##########################
# HTTP processing errors #
##########################

# invalid JSON object
HTTP_CORRUPTED_JSON = 600

# superfluous URL suffices
HTTP_SUPERFLUOUS_SUFFICES = 601

####################################
# Internal ArangoDB storage errors #
####################################

# illegal state
ILLEGAL_STATE = 1000

# read only
READ_ONLY = 1004

# duplicate identifier
DUPLICATE_IDENTIFIER = 1005

####################################
# External ArangoDB storage errors #
####################################

# corrupted datafile
CORRUPTED_DATAFILE = 1100

# illegal or unreadable parameter file
ILLEGAL_PARAMETER_FILE = 1101

# corrupted collection
CORRUPTED_COLLECTION = 1102

# filesystem full
FILESYSTEM_FULL = 1104

# database directory is locked
DATADIR_LOCKED = 1107

###################################
# General ArangoDB storage errors #
###################################

# conflict
CONFLICT = 1200

# document not found
DOCUMENT_NOT_FOUND = 1202

# collection or view not found
DATA_SOURCE_NOT_FOUND = 1203

# parameter 'collection' not found
COLLECTION_PARAMETER_MISSING = 1204

# illegal document identifier
DOCUMENT_HANDLE_BAD = 1205

# duplicate name
DUPLICATE_NAME = 1207

# illegal name
ILLEGAL_NAME = 1208

# no suitable index known
NO_INDEX = 1209

# unique constraint violated
UNIQUE_CONSTRAINT_VIOLATED = 1210

# index not found
INDEX_NOT_FOUND = 1212

# cross collection request not allowed
CROSS_COLLECTION_REQUEST = 1213

# illegal index identifier
INDEX_HANDLE_BAD = 1214

# document too large
DOCUMENT_TOO_LARGE = 1216

# collection type invalid
COLLECTION_TYPE_INVALID = 1218

# parsing attribute name definition failed
ATTRIBUTE_PARSER_FAILED = 1220

# illegal document key
DOCUMENT_KEY_BAD = 1221

# unexpected document key
DOCUMENT_KEY_UNEXPECTED = 1222

# server database directory not writable
DATADIR_NOT_WRITABLE = 1224

# out of keys
OUT_OF_KEYS = 1225

# missing document key
DOCUMENT_KEY_MISSING = 1226

# invalid document type
DOCUMENT_TYPE_INVALID = 1227

# database not found
DATABASE_NOT_FOUND = 1228

# database name invalid
DATABASE_NAME_INVALID = 1229

# operation only allowed in system database
USE_SYSTEM_DATABASE = 1230

# invalid key generator
INVALID_KEY_GENERATOR = 1232

# expecting both `_from` and `_to` attributes to be defined in the edge document and have the format `<collectionName>/<vertexKey>`
INVALID_EDGE_ATTRIBUTE = 1233

# index creation failed
INDEX_CREATION_FAILED = 1235

# collection type mismatch
COLLECTION_TYPE_MISMATCH = 1237

# collection not loaded
COLLECTION_NOT_LOADED = 1238

# illegal document revision
DOCUMENT_REV_BAD = 1239

# incomplete read
INCOMPLETE_READ = 1240

# not supported by old legacy data format
OLD_ROCKSDB_FORMAT = 1241

# an index with legacy sorted keys has been found
INDEX_HAS_LEGACY_SORTED_KEYS = 1242

###################################
# Checked ArangoDB storage errors #
###################################

# server database directory is empty
EMPTY_DATADIR = 1301

# operation should be tried again
TRY_AGAIN = 1302

# engine is busy
BUSY = 1303

# merge in progress
MERGE_IN_PROGRESS = 1304

# storage engine I/O error
IO_ERROR = 1305

###############################
# ArangoDB replication errors #
###############################

# no response
REPLICATION_NO_RESPONSE = 1400

# invalid response
REPLICATION_INVALID_RESPONSE = 1401

# leader error
REPLICATION_LEADER_ERROR = 1402

# leader incompatible
REPLICATION_LEADER_INCOMPATIBLE = 1403

# leader change
REPLICATION_LEADER_CHANGE = 1404

# loop detected
REPLICATION_LOOP = 1405

# unexpected marker
REPLICATION_UNEXPECTED_MARKER = 1406

# invalid applier state
REPLICATION_INVALID_APPLIER_STATE = 1407

# invalid transaction
REPLICATION_UNEXPECTED_TRANSACTION = 1408

# shard synchronization attempt timeout exceeded
REPLICATION_SHARD_SYNC_ATTEMPT_TIMEOUT_EXCEEDED = 1409

# invalid replication applier configuration
REPLICATION_INVALID_APPLIER_CONFIGURATION = 1410

# cannot perform operation while applier is running
REPLICATION_RUNNING = 1411

# replication stopped
REPLICATION_APPLIER_STOPPED = 1412

# no start tick
REPLICATION_NO_START_TICK = 1413

# start tick not present
REPLICATION_START_TICK_NOT_PRESENT = 1414

# wrong checksum
REPLICATION_WRONG_CHECKSUM = 1416

# shard not empty
REPLICATION_SHARD_NONEMPTY = 1417

# replicated log {} not found
REPLICATION_REPLICATED_LOG_NOT_FOUND = 1418

# not the log leader
REPLICATION_REPLICATED_LOG_NOT_THE_LEADER = 1419

# not a log follower
REPLICATION_REPLICATED_LOG_NOT_A_FOLLOWER = 1420

# follower rejected append entries request
REPLICATION_REPLICATED_LOG_APPEND_ENTRIES_REJECTED = 1421

# a resigned leader instance rejected a request
REPLICATION_REPLICATED_LOG_LEADER_RESIGNED = 1422

# a resigned follower instance rejected a request
REPLICATION_REPLICATED_LOG_FOLLOWER_RESIGNED = 1423

# the replicated log of the participant is gone
REPLICATION_REPLICATED_LOG_PARTICIPANT_GONE = 1424

# an invalid term was given
REPLICATION_REPLICATED_LOG_INVALID_TERM = 1425

# log participant unconfigured
REPLICATION_REPLICATED_LOG_UNCONFIGURED = 1426

# replicated state {id:} of type {type:} not found
REPLICATION_REPLICATED_STATE_NOT_FOUND = 1427

# replicated state {id:} of type {type:} is unavailable
REPLICATION_REPLICATED_STATE_NOT_AVAILABLE = 1428

# not enough replicas for the configured write-concern are present
REPLICATION_WRITE_CONCERN_NOT_FULFILLED = 1429

# operation aborted because a previous operation failed
REPLICATION_REPLICATED_LOG_SUBSEQUENT_FAULT = 1430

# replicated state type {type:} is unavailable
REPLICATION_REPLICATED_STATE_IMPLEMENTATION_NOT_FOUND = 1431

# error in the replicated WAL subsystem
REPLICATION_REPLICATED_WAL_ERROR = 1432

# replicated WAL {file:} has an invalid or missing file header
REPLICATION_REPLICATED_WAL_INVALID_FILE = 1433

# replicated WAL {file:} is corrupt
REPLICATION_REPLICATED_WAL_CORRUPT = 1434

###########################
# ArangoDB cluster errors #
###########################

# not a follower
CLUSTER_NOT_FOLLOWER = 1446

# follower transaction intermediate commit already performed
CLUSTER_FOLLOWER_TRANSACTION_COMMIT_PERFORMED = 1447

# creating collection failed due to precondition
CLUSTER_CREATE_COLLECTION_PRECONDITION_FAILED = 1448

# got a request from an unknown server
CLUSTER_SERVER_UNKNOWN = 1449

# too many shards
CLUSTER_TOO_MANY_SHARDS = 1450

# could not create collection in plan
CLUSTER_COULD_NOT_CREATE_COLLECTION_IN_PLAN = 1454

# could not create collection
CLUSTER_COULD_NOT_CREATE_COLLECTION = 1456

# timeout in cluster operation
CLUSTER_TIMEOUT = 1457

# could not remove collection from plan
CLUSTER_COULD_NOT_REMOVE_COLLECTION_IN_PLAN = 1458

# could not create database in plan
CLUSTER_COULD_NOT_CREATE_DATABASE_IN_PLAN = 1460

# could not create database
CLUSTER_COULD_NOT_CREATE_DATABASE = 1461

# could not remove database from plan
CLUSTER_COULD_NOT_REMOVE_DATABASE_IN_PLAN = 1462

# could not remove database from current
CLUSTER_COULD_NOT_REMOVE_DATABASE_IN_CURRENT = 1463

# no responsible shard found
CLUSTER_SHARD_GONE = 1464

# cluster internal HTTP connection broken
CLUSTER_CONNECTION_LOST = 1465

# must not specify _key for this collection
CLUSTER_MUST_NOT_SPECIFY_KEY = 1466

# got contradicting answers from different shards
CLUSTER_GOT_CONTRADICTING_ANSWERS = 1467

# not all sharding attributes given
CLUSTER_NOT_ALL_SHARDING_ATTRIBUTES_GIVEN = 1468

# must not change the value of a shard key attribute
CLUSTER_MUST_NOT_CHANGE_SHARDING_ATTRIBUTES = 1469

# unsupported operation or parameter for clusters
CLUSTER_UNSUPPORTED = 1470

# this operation is only valid on a coordinator in a cluster
CLUSTER_ONLY_ON_COORDINATOR = 1471

# error reading Plan in agency
CLUSTER_READING_PLAN_AGENCY = 1472

# error in cluster internal communication for AQL
CLUSTER_AQL_COMMUNICATION = 1474

# this operation is only valid on a DBserver in a cluster
CLUSTER_ONLY_ON_DBSERVER = 1477

# A cluster backend which was required for the operation could not be reached
CLUSTER_BACKEND_UNAVAILABLE = 1478

# collection/view is out of sync
CLUSTER_AQL_COLLECTION_OUT_OF_SYNC = 1481

# could not create index in plan
CLUSTER_COULD_NOT_CREATE_INDEX_IN_PLAN = 1482

# could not drop index in plan
CLUSTER_COULD_NOT_DROP_INDEX_IN_PLAN = 1483

# chain of distributeShardsLike references
CLUSTER_CHAIN_OF_DISTRIBUTESHARDSLIKE = 1484

# must not drop collection while another has a distributeShardsLike attribute pointing to it
CLUSTER_MUST_NOT_DROP_COLL_OTHER_DISTRIBUTESHARDSLIKE = 1485

# must not have a distributeShardsLike attribute pointing to an unknown collection
CLUSTER_UNKNOWN_DISTRIBUTESHARDSLIKE = 1486

# the number of current DB-Servers is lower than the requested replicationFactor/writeConcern
CLUSTER_INSUFFICIENT_DBSERVERS = 1487

# a follower could not be dropped in agency
CLUSTER_COULD_NOT_DROP_FOLLOWER = 1488

# a shard leader refuses to perform a replication operation
CLUSTER_SHARD_LEADER_REFUSES_REPLICATION = 1489

# a shard follower refuses to perform an operation
CLUSTER_SHARD_FOLLOWER_REFUSES_OPERATION = 1490

# a (former) shard leader refuses to perform an operation
CLUSTER_SHARD_LEADER_RESIGNED = 1491

# some agency operation failed
CLUSTER_AGENCY_COMMUNICATION_FAILED = 1492

# leadership challenge is ongoing
CLUSTER_LEADERSHIP_CHALLENGE_ONGOING = 1495

# not a leader
CLUSTER_NOT_LEADER = 1496

# could not create view in plan
CLUSTER_COULD_NOT_CREATE_VIEW_IN_PLAN = 1497

# view ID already exists
CLUSTER_VIEW_ID_EXISTS = 1498

# could not drop collection in plan
CLUSTER_COULD_NOT_DROP_COLLECTION = 1499

#########################
# ArangoDB query errors #
#########################

# query killed
QUERY_KILLED = 1500

# %s
QUERY_PARSE = 1501

# query is empty
QUERY_EMPTY = 1502

# runtime error '%s'
QUERY_SCRIPT = 1503

# number out of range
QUERY_NUMBER_OUT_OF_RANGE = 1504

# invalid geo coordinate value
QUERY_INVALID_GEO_VALUE = 1505

# variable name '%s' has an invalid format
QUERY_VARIABLE_NAME_INVALID = 1510

# variable '%s' is assigned multiple times
QUERY_VARIABLE_REDECLARED = 1511

# unknown variable '%s'
QUERY_VARIABLE_NAME_UNKNOWN = 1512

# unable to read-lock collection %s
QUERY_COLLECTION_LOCK_FAILED = 1521

# too many collections/shards
QUERY_TOO_MANY_COLLECTIONS = 1522

# too much nesting or too many objects
QUERY_TOO_MUCH_NESTING = 1524

# unknown/invalid OPTIONS attribute used
QUERY_INVALID_OPTIONS_ATTRIBUTE = 1539

# usage of unknown function '%s()'
QUERY_FUNCTION_NAME_UNKNOWN = 1540

# invalid number of arguments for function '%s()'
QUERY_FUNCTION_ARGUMENT_NUMBER_MISMATCH = 1541

# invalid argument type in call to function '%s()'
QUERY_FUNCTION_ARGUMENT_TYPE_MISMATCH = 1542

# invalid regex value
QUERY_INVALID_REGEX = 1543

# invalid structure of bind parameters
QUERY_BIND_PARAMETERS_INVALID = 1550

# no value specified for declared bind parameter '%s'
QUERY_BIND_PARAMETER_MISSING = 1551

# bind parameter '%s' was not declared in the query
QUERY_BIND_PARAMETER_UNDECLARED = 1552

# bind parameter '%s' has an invalid value or type
QUERY_BIND_PARAMETER_TYPE = 1553

# failed vector search
QUERY_VECTOR_SEARCH_NOT_APPLIED = 1554

# invalid arithmetic value
QUERY_INVALID_ARITHMETIC_VALUE = 1561

# division by zero
QUERY_DIVISION_BY_ZERO = 1562

# array expected
QUERY_ARRAY_EXPECTED = 1563

# collection '%s' used as expression operand
QUERY_COLLECTION_USED_IN_EXPRESSION = 1568

# FAIL(%s) called
QUERY_FAIL_CALLED = 1569

# no suitable geo index found for geo restriction on '%s'
QUERY_GEO_INDEX_MISSING = 1570

# no suitable fulltext index found for fulltext query on '%s'
QUERY_FULLTEXT_INDEX_MISSING = 1571

# invalid date value
QUERY_INVALID_DATE_VALUE = 1572

# multi-modify query
QUERY_MULTI_MODIFY = 1573

# invalid aggregate expression
QUERY_INVALID_AGGREGATE_EXPRESSION = 1574

# query options must be readable at query compile time
QUERY_COMPILE_TIME_OPTIONS = 1575

# FILTER/PRUNE condition complexity is too high
QUERY_DNF_COMPLEXITY = 1576

# could not use forced index hint
QUERY_FORCED_INDEX_HINT_UNUSABLE = 1577

# disallowed dynamic call to '%s'
QUERY_DISALLOWED_DYNAMIC_CALL = 1578

# access after data-modification by %s
QUERY_ACCESS_AFTER_MODIFICATION = 1579

############################
# AQL user function errors #
############################

# invalid user function name
QUERY_FUNCTION_INVALID_NAME = 1580

# invalid user function code
QUERY_FUNCTION_INVALID_CODE = 1581

# user function '%s()' not found
QUERY_FUNCTION_NOT_FOUND = 1582

# user function runtime error: %s
QUERY_FUNCTION_RUNTIME_ERROR = 1583

# query is not eligible for plan caching
QUERY_NOT_ELIGIBLE_FOR_PLAN_CACHING = 1584

#############################
# AQL query registry errors #
#############################

# bad execution plan JSON
QUERY_BAD_JSON_PLAN = 1590

# query ID not found
QUERY_NOT_FOUND = 1591

# %s
QUERY_USER_ASSERT = 1593

# %s
QUERY_USER_WARN = 1594

# window operation after data-modification
QUERY_WINDOW_AFTER_MODIFICATION = 1595

##########################
# ArangoDB cursor errors #
##########################

# cursor not found
CURSOR_NOT_FOUND = 1600

# cursor is busy
CURSOR_BUSY = 1601

#####################################
# ArangoDB schema validation errors #
#####################################

# schema validation failed
VALIDATION_FAILED = 1620

# invalid schema validation parameter
VALIDATION_BAD_PARAMETER = 1621

###############################
# ArangoDB transaction errors #
###############################

# internal transaction error
TRANSACTION_INTERNAL = 1650

# nested transactions detected
TRANSACTION_NESTED = 1651

# unregistered collection used in transaction
TRANSACTION_UNREGISTERED_COLLECTION = 1652

# disallowed operation inside transaction
TRANSACTION_DISALLOWED_OPERATION = 1653

# transaction aborted
TRANSACTION_ABORTED = 1654

# transaction not found
TRANSACTION_NOT_FOUND = 1655

##########################
# User management errors #
##########################

# invalid user name
USER_INVALID_NAME = 1700

# duplicate user
USER_DUPLICATE = 1702

# user not found
USER_NOT_FOUND = 1703

# user is external
USER_EXTERNAL = 1705

######################################
# Service management errors (legacy) #
######################################

# service download failed
SERVICE_DOWNLOAD_FAILED = 1752

# service upload failed
SERVICE_UPLOAD_FAILED = 1753

###############
# Task errors #
###############

# invalid task id
TASK_INVALID_ID = 1850

# duplicate task id
TASK_DUPLICATE_ID = 1851

# task not found
TASK_NOT_FOUND = 1852

############################
# Graph / traversal errors #
############################

# invalid graph
GRAPH_INVALID_GRAPH = 1901

# invalid edge
GRAPH_INVALID_EDGE = 1906

# invalid filter result
GRAPH_INVALID_FILTER_RESULT = 1910

# multi use of edge collection in edge def
GRAPH_COLLECTION_MULTI_USE = 1920

# edge collection already used in edge def
GRAPH_COLLECTION_USE_IN_MULTI_GRAPHS = 1921

# missing graph name
GRAPH_CREATE_MISSING_NAME = 1922

# malformed edge definition
GRAPH_CREATE_MALFORMED_EDGE_DEFINITION = 1923

# graph '%s' not found
GRAPH_NOT_FOUND = 1924

# graph already exists
GRAPH_DUPLICATE = 1925

# vertex collection does not exist or is not part of the graph
GRAPH_VERTEX_COL_DOES_NOT_EXIST = 1926

# collection not a vertex collection
GRAPH_WRONG_COLLECTION_TYPE_VERTEX = 1927

# collection is not in list of orphan collections
GRAPH_NOT_IN_ORPHAN_COLLECTION = 1928

# collection already used in edge def
GRAPH_COLLECTION_USED_IN_EDGE_DEF = 1929

# edge collection not used in graph
GRAPH_EDGE_COLLECTION_NOT_USED = 1930

# collection _graphs does not exist
GRAPH_NO_GRAPH_COLLECTION = 1932

# Invalid number of arguments. Expected:
GRAPH_INVALID_NUMBER_OF_ARGUMENTS = 1935

# Invalid parameter type.
GRAPH_INVALID_PARAMETER = 1936

# collection used in orphans
GRAPH_COLLECTION_USED_IN_ORPHANS = 1938

# edge collection does not exist or is not part of the graph
GRAPH_EDGE_COL_DOES_NOT_EXIST = 1939

# empty graph
GRAPH_EMPTY = 1940

# internal graph data corrupt
GRAPH_INTERNAL_DATA_CORRUPT = 1941

# must not drop collection while part of graph
GRAPH_MUST_NOT_DROP_COLLECTION = 1942

# malformed orphan list
GRAPH_CREATE_MALFORMED_ORPHAN_LIST = 1943

# edge definition collection is a document collection
GRAPH_EDGE_DEFINITION_IS_DOCUMENT = 1944

# initial collection is not allowed to be removed manually
GRAPH_COLLECTION_IS_INITIAL = 1945

# no valid initial collection found
GRAPH_NO_INITIAL_COLLECTION = 1946

# referenced vertex collection is not part of the graph
GRAPH_REFERENCED_VERTEX_COLLECTION_NOT_PART_OF_THE_GRAPH = 1947

# negative edge weight found
GRAPH_NEGATIVE_EDGE_WEIGHT = 1948

# the given collection is not part of the graph
GRAPH_COLLECTION_NOT_PART_OF_THE_GRAPH = 1949

##################
# Session errors #
##################

# unknown session
SESSION_UNKNOWN = 1950

# session expired
SESSION_EXPIRED = 1951

########################
# Simple Client errors #
########################

# unknown client error
SIMPLE_CLIENT_UNKNOWN_ERROR = 2000

# could not connect to server
SIMPLE_CLIENT_COULD_NOT_CONNECT = 2001

# could not write to server
SIMPLE_CLIENT_COULD_NOT_WRITE = 2002

# could not read from server
SIMPLE_CLIENT_COULD_NOT_READ = 2003

# was erlaube?!
WAS_ERLAUBE = 2019

#######################
# internal AQL errors #
#######################

# General internal AQL error
INTERNAL_AQL = 2200

##########################
# Foxx management errors #
##########################

# failed to parse manifest file
MALFORMED_MANIFEST_FILE = 3000

# manifest file is invalid
INVALID_SERVICE_MANIFEST = 3001

# service files missing
SERVICE_FILES_MISSING = 3002

# service files outdated
SERVICE_FILES_OUTDATED = 3003

# service options are invalid
INVALID_FOXX_OPTIONS = 3004

# invalid mountpath
INVALID_MOUNTPOINT = 3007

# service not found
SERVICE_NOT_FOUND = 3009

# service needs configuration
SERVICE_NEEDS_CONFIGURATION = 3010

# service already exists
SERVICE_MOUNTPOINT_CONFLICT = 3011

# missing manifest file
SERVICE_MANIFEST_NOT_FOUND = 3012

# failed to parse service options
SERVICE_OPTIONS_MALFORMED = 3013

# source path not found
SERVICE_SOURCE_NOT_FOUND = 3014

# error resolving source
SERVICE_SOURCE_ERROR = 3015

# unknown script
SERVICE_UNKNOWN_SCRIPT = 3016

# service api disabled
SERVICE_API_DISABLED = 3099

###################################
# JavaScript module loader errors #
###################################

# cannot locate module
MODULE_NOT_FOUND = 3100

# syntax error in module
MODULE_SYNTAX_ERROR = 3101

# failed to invoke module
MODULE_FAILURE = 3103

#############################
# Enterprise Edition errors #
#############################

# collection is not smart
NO_SMART_COLLECTION = 4000

# smart graph attribute not given
NO_SMART_GRAPH_ATTRIBUTE = 4001

# cannot drop this smart collection
CANNOT_DROP_SMART_COLLECTION = 4002

# in smart vertex collections _key must be a string and prefixed with the value of the smart graph attribute
KEY_MUST_BE_PREFIXED_WITH_SMART_GRAPH_ATTRIBUTE = 4003

# attribute cannot be used as smart graph attribute
ILLEGAL_SMART_GRAPH_ATTRIBUTE = 4004

# smart graph attribute mismatch
SMART_GRAPH_ATTRIBUTE_MISMATCH = 4005

# invalid smart join attribute declaration
INVALID_SMART_JOIN_ATTRIBUTE = 4006

# shard key value must be prefixed with the value of the smart join attribute
KEY_MUST_BE_PREFIXED_WITH_SMART_JOIN_ATTRIBUTE = 4007

# smart join attribute not given or invalid
NO_SMART_JOIN_ATTRIBUTE = 4008

# must not change the value of the smartJoinAttribute
CLUSTER_MUST_NOT_CHANGE_SMART_JOIN_ATTRIBUTE = 4009

# non disjoint edge found
INVALID_DISJOINT_SMART_EDGE = 4010

# Unsupported alternating Smart and Satellite in Disjoint SmartGraph.
UNSUPPORTED_CHANGE_IN_SMART_TO_SATELLITE_DISJOINT_EDGE_DIRECTION = 4011

#################
# Agency errors #
#################

# malformed gossip message
AGENCY_MALFORMED_GOSSIP_MESSAGE = 20001

# malformed inquire request
AGENCY_MALFORMED_INQUIRE_REQUEST = 20002

# Inform message must be an object.
AGENCY_INFORM_MUST_BE_OBJECT = 20011

# Inform message must contain uint parameter 'term'
AGENCY_INFORM_MUST_CONTAIN_TERM = 20012

# Inform message must contain string parameter 'id'
AGENCY_INFORM_MUST_CONTAIN_ID = 20013

# Inform message must contain array 'active'
AGENCY_INFORM_MUST_CONTAIN_ACTIVE = 20014

# Inform message must contain object 'pool'
AGENCY_INFORM_MUST_CONTAIN_POOL = 20015

# Inform message must contain object 'min ping'
AGENCY_INFORM_MUST_CONTAIN_MIN_PING = 20016

# Inform message must contain object 'max ping'
AGENCY_INFORM_MUST_CONTAIN_MAX_PING = 20017

# Inform message must contain object 'timeoutMult'
AGENCY_INFORM_MUST_CONTAIN_TIMEOUT_MULT = 20018

# Cannot rebuild readDB and spearHead
AGENCY_CANNOT_REBUILD_DBS = 20021

# malformed agency transaction
AGENCY_MALFORMED_TRANSACTION = 20030

######################
# Supervision errors #
######################

# general supervision failure
SUPERVISION_GENERAL_FAILURE = 20501

####################
# Scheduler errors #
####################

# queue is full
QUEUE_FULL = 21003

# queue time violated
QUEUE_TIME_REQUIREMENT_VIOLATED = 21004

# too many detached scheduler threads
TOO_MANY_DETACHED_THREADS = 21005

######################
# Maintenance errors #
######################

# maintenance action still processing
ACTION_UNFINISHED = 6003

#########################
# Backup/Restore errors #
#########################

# internal hot backup error
HOT_BACKUP_INTERNAL = 7001

# internal hot restore error
HOT_RESTORE_INTERNAL = 7002

# backup does not match this topology
BACKUP_TOPOLOGY = 7003

# no space left on device
NO_SPACE_LEFT_ON_DEVICE = 7004

# failed to upload hot backup set to remote target
FAILED_TO_UPLOAD_BACKUP = 7005

# failed to download hot backup set from remote source
FAILED_TO_DOWNLOAD_BACKUP = 7006

# no such hot backup set can be found
NO_SUCH_HOT_BACKUP = 7007

# remote hotback repository configuration error
REMOTE_REPOSITORY_CONFIG_BAD = 7008

# some db servers cannot be reached for transaction locks
LOCAL_LOCK_FAILED = 7009

# some db servers cannot be reached for transaction locks
LOCAL_LOCK_RETRY = 7010

# hot backup conflict
HOT_BACKUP_CONFLICT = 7011

# hot backup not all db servers reachable
HOT_BACKUP_DBSERVERS_AWOL = 7012

#########################
# Plan Analyzers errors #
#########################

# analyzers in plan could not be modified
CLUSTER_COULD_NOT_MODIFY_ANALYZERS_IN_PLAN = 7021

#############
# Licensing #
#############

# license has expired or is invalid
LICENSE_EXPIRED_OR_INVALID = 9001

# license verification failed
LICENSE_SIGNATURE_VERIFICATION = 9002

# non-matching license id
LICENSE_NON_MATCHING_ID = 9003

# feature is not enabled by the license
LICENSE_FEATURE_NOT_ENABLED = 9004

# the resource is exhausted
LICENSE_RESOURCE_EXHAUSTED = 9005

# invalid license
LICENSE_INVALID = 9006

# conflicting license
LICENSE_CONFLICT = 9007

# failed to validate license signature
LICENSE_VALIDATION_FAILED = 9008
