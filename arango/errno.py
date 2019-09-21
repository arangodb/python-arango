##################
# General Errors #
##################

# No error occurred.
NO_ERROR = 0

# General error occurred.
FAILED = 1

# Operating system error occurred.
SYS_ERROR = 2

# Out of memory.
OUT_OF_MEMORY = 3

# Internal error occurred.
INTERNAL = 4

# Illegal number representation given.
ILLEGAL_NUMBER = 5

# Numeric overflow occurred.
NUMERIC_OVERFLOW = 6

# Unknown option supplied by user.
ILLEGAL_OPTION = 7

# Detected PID without living process.
DEAD_PID = 8

# Feature not implemented.
NOT_IMPLEMENTED = 9

# Bad parameter.
BAD_PARAMETER = 10

# Missing permission.
FORBIDDEN = 11

# Out of memory (mmap).
OUT_OF_MEMORY_MMAP = 12

# Corrupt CSV line.
CORRUPTED_CSV = 13

# File not found.
FILE_NOT_FOUND = 14

# Cannot write to file.
CANNOT_WRITE_FILE = 15

# Cannot overwrite file.
CANNOT_OVERWRITE_FILE = 16

# Type error occurred.
TYPE_ERROR = 17

# Timed out waiting for a lock.
LOCK_TIMEOUT = 18

# Cannot create a directory.
CANNOT_CREATE_DIRECTORY = 19

# Cannot create a temporary file.
CANNOT_CREATE_TEMP_FILE = 20

# Request cancelled by user.
REQUEST_CANCELED = 21

# Raised for debugging.
DEBUG = 22

# Invalid IP address.
IP_ADDRESS_INVALID = 25

# File exists already.
FILE_EXISTS = 27

# Locked resource or operation.
LOCKED = 28

# Deadlock detected when accessing collections.
DEADLOCK = 29

# Call failed as server shutdown is in progress.
SHUTTING_DOWN = 30

# Feature only for enterprise version of ArangoDB.
ONLY_ENTERPRISE = 31

# Resource usage exceeded maximum value.
RESOURCE_LIMIT = 32

# ICU operation failed.
ICU_ERROR = 33

# Cannot read a file.
CANNOT_READ_FILE = 34

# Incompatible version of ArangoDB.
INCOMPATIBLE_VERSION = 35

# Requested resource disabled.
DISABLED = 36

###########################
# HTTP Error Status Codes #
###########################

# Bad HTTP parameter.
HTTP_BAD_PARAMETER = 400

# User unauthorized.
HTTP_UNAUTHORIZED = 401

# Operation forbidden.
HTTP_FORBIDDEN = 403

# Unknown URI.
HTTP_NOT_FOUND = 404

# HTTP method unknown.
HTTP_METHOD_NOT_ALLOWED = 405

# HTTP content type not supported.
HTTP_NOT_ACCEPTABLE = 406

# Precondition not met.
HTTP_PRECONDITION_FAILED = 412

# Internal server error occurred.
HTTP_SERVER_ERROR = 500

# Service temporarily unavailable.
HTTP_SERVICE_UNAVAILABLE = 503

# Service contacted by ArangoDB did not respond in time.
HTTP_GATEWAY_TIMEOUT = 504

##########################
# HTTP Processing Errors #
##########################

# Corrupted JSON string.
HTTP_CORRUPTED_JSON = 600

# URL contains superfluous suffices.
HTTP_SUPERFLUOUS_SUFFICES = 601

####################################
# Internal ArangoDB Storage Errors #
####################################

# Datafile in illegal state.
ILLEGAL_STATE = 1000

# User attempted to write to a sealed datafile.
DATAFILE_SEALED = 1002

# Read-only datafile or collection.
READ_ONLY = 1004

# Duplicate identifier detected.
DUPLICATE_IDENTIFIER = 1005

# Datafile unreadable.
DATAFILE_UNREADABLE = 1006

# Datafile empty.
DATAFILE_EMPTY = 1007

# Error occurred during WAL log file recovery.
RECOVERY = 1008

# Required datafile statistics object not found.
DATAFILE_STATISTICS_NOT_FOUND = 1009

####################################
# External ArangoDB Storage Errors #
####################################

# Datafile corrupted.
CORRUPTED_DATAFILE = 1100

# Parameter file corrupted or cannot be read.
ILLEGAL_PARAMETER_FILE = 1101

# Collection contains one or more corrupted datafiles.
CORRUPTED_COLLECTION = 1102

# System call mmap failed.
MMAP_FAILED = 1103

# Filesystem full.
FILESYSTEM_FULL = 1104

# Cannot create journal.
NO_JOURNAL = 1105

# Datafile of the same name already exists.
DATAFILE_ALREADY_EXISTS = 1106

# Database directory locked by another process.
DATADIR_LOCKED = 1107

# Directory of the same name already exists.
COLLECTION_DIRECTORY_ALREADY_EXISTS = 1108

# System call msync failed.
MSYNC_FAILED = 1109

# Cannot lock the database directory on startup.
DATADIR_UNLOCKABLE = 1110

# Server waited too long for the datafile to be synced to disk.
SYNC_TIMEOUT = 1111

###################################
# General ArangoDB Storage Errors #
###################################

# Conflict detected while updating or deleting a document.
CONFLICT = 1200

# Database directory invalid.
DATADIR_INVALID = 1201

# Unknown document identifier or handle.
DOCUMENT_NOT_FOUND = 1202

# Collection with given identifier or name unknown.
DATA_SOURCE_NOT_FOUND = 1203

# Missing collection parameter.
COLLECTION_PARAMETER_MISSING = 1204

# Invalid document handle.
DOCUMENT_HANDLE_BAD = 1205

# Maximal journal size too small.
MAXIMAL_SIZE_TOO_SMALL = 1206

# Duplicate name detected.
DUPLICATE_NAME = 1207

# Illegal name detected.
ILLEGAL_NAME = 1208

# No suitable index for query.
NO_INDEX = 1209

# Unique constraint violation.
UNIQUE_CONSTRAINT_VIOLATED = 1210

# Index with unknown identifier.
INDEX_NOT_FOUND = 1212

# Cross-collection requested.
CROSS_COLLECTION_REQUEST = 1213

# Index handle corrupted.
INDEX_HANDLE_BAD = 1214

# Document too large to fit into any datafile.
DOCUMENT_TOO_LARGE = 1216

# Collection must be unloaded.
COLLECTION_NOT_UNLOADED = 1217

# Invalid collection type.
COLLECTION_TYPE_INVALID = 1218

# Failed to parse an attribute name definition.
ATTRIBUTE_PARSER_FAILED = 1220

# Corrupted document key.
DOCUMENT_KEY_BAD = 1221

# User-defined document key supplied for collections with auto key generation.
DOCUMENT_KEY_UNEXPECTED = 1222

# Database directory not writable for current user.
DATADIR_NOT_WRITABLE = 1224

# Key generator out of keys.
OUT_OF_KEYS = 1225

# Document key missing.
DOCUMENT_KEY_MISSING = 1226

# There was an attempt to create a document of invalid type.
DOCUMENT_TYPE_INVALID = 1227

# Non-existing database accessed.
DATABASE_NOT_FOUND = 1228

# Invalid database used.
DATABASE_NAME_INVALID = 1229

# Operation requested in non-system database.
USE_SYSTEM_DATABASE = 1230

# Invalid key generator.
INVALID_KEY_GENERATOR = 1232

# Undefined or invalid "_from" or "_to" values in an edge document.
INVALID_EDGE_ATTRIBUTE = 1233

# Cannot create index.
INDEX_CREATION_FAILED = 1235

# Server is write-throttled and a write operation waited too long.
WRITE_THROTTLE_TIMEOUT = 1236

# Collection type mismatch.
COLLECTION_TYPE_MISMATCH = 1237

# Collection accessed but not yet loaded.
COLLECTION_NOT_LOADED = 1238

# Document revision corrupt or missing.
DOCUMENT_REV_BAD = 1239

# Read cannot be completed by storage engine.
INCOMPLETE_READ = 1240

###################################
# Checked ArangoDB Storage Errors #
###################################

# Datafile full.
DATAFILE_FULL = 1300

# Server database directory empty.
EMPTY_DATADIR = 1301

# Operation needs to be retried.
TRY_AGAIN = 1302

# Storage engine busy.
BUSY = 1303

# Datafile merge in progress and the operation cannot be completed.
MERGE_IN_PROGRESS = 1304

# Storage engine encountered an I/O error.
IO_ERROR = 1305

###############################
# ArangoDB Replication Errors #
###############################

# Replication applier received no (or incomplete) response from master.
REPLICATION_NO_RESPONSE = 1400

# Replication applier received an invalid response from master.
REPLICATION_INVALID_RESPONSE = 1401

# Replication applier received a server error from master.
REPLICATION_MASTER_ERROR = 1402

# Replication applier tried to connect to master with incompatible version.
REPLICATION_MASTER_INCOMPATIBLE = 1403

# Replication applier connected to a different master than before.
REPLICATION_MASTER_CHANGE = 1404

# Replication applier was asked to connect to itself for replication.
REPLICATION_LOOP = 1405

# Unexpected marker found in replication log stream.
REPLICATION_UNEXPECTED_MARKER = 1406

# Found invalid replication applier state file.
REPLICATION_INVALID_APPLIER_STATE = 1407

# Found unexpected transaction ID.
REPLICATION_UNEXPECTED_TRANSACTION = 1408

# Invalid replication applier configuration.
REPLICATION_INVALID_APPLIER_CONFIGURATION = 1410

# Operation attempted while replication applier is running.
REPLICATION_RUNNING = 1411

# Replication applier stopped by user.
REPLICATION_APPLIER_STOPPED = 1412

# Replication applier started without a known start tick value.
REPLICATION_NO_START_TICK = 1413

# Replication applier started without a known start tick value.
REPLICATION_START_TICK_NOT_PRESENT = 1414

# Newborn follower submits a wrong checksum.
REPLICATION_WRONG_CHECKSUM = 1416

# Shard is not empty and follower tries a shortcut.
REPLICATION_SHARD_NONEMPTY = 1417

###########################
# ArangoDB Cluster Errors #
###########################

# Raised on some occasions when one server gets a request from another.
CLUSTER_SERVER_UNKNOWN = 1449

# Coordinator cannot create a collection as the collection ID already exists.
CLUSTER_COLLECTION_ID_EXISTS = 1453

# Coordinator cannot create an entry for a new collection in Plan hierarchy.
CLUSTER_COULD_NOT_CREATE_COLLECTION_IN_PLAN = 1454

# Coordinator sees DBServer issues when creating shards for a new collection.
CLUSTER_COULD_NOT_CREATE_COLLECTION = 1456

# Coordinator runs into a timeout for some cluster wide operation.
CLUSTER_TIMEOUT = 1457

# Coordinator cannot remove an entry for a collection in Plan hierarchy.
CLUSTER_COULD_NOT_REMOVE_COLLECTION_IN_PLAN = 1458

# Coordinator cannot remove an entry for a collection in Current hierarchy.
CLUSTER_COULD_NOT_REMOVE_COLLECTION_IN_CURRENT = 1459

# Coordinator cannot create an entry for a new database in the Plan hierarchy.
CLUSTER_COULD_NOT_CREATE_DATABASE_IN_PLAN = 1460

# Coordinator sees DBServer issues when creating databases for a new cluster.
CLUSTER_COULD_NOT_CREATE_DATABASE = 1461

# Coordinator cannot remove an entry for a database in the Plan hierarchy.
CLUSTER_COULD_NOT_REMOVE_DATABASE_IN_PLAN = 1462

# Coordinator cannot remove an entry for a database in the Current hierarchy.
CLUSTER_COULD_NOT_REMOVE_DATABASE_IN_CURRENT = 1463

# Coordinator cannot determine the shard responsible for a given document.
CLUSTER_SHARD_GONE = 1464

# Coordinator loses HTTP connection to a DBServer while transferring data.
CLUSTER_CONNECTION_LOST = 1465

# "_key" attribute specified in sharded collection which uses not only "_key"
# as sharding attribute.
CLUSTER_MUST_NOT_SPECIFY_KEY = 1466

# Coordinator gets conflicting results from different shards.
CLUSTER_GOT_CONTRADICTING_ANSWERS = 1467

# Coordinator tries to find out the shard responsible for a partial document.
CLUSTER_NOT_ALL_SHARDING_ATTRIBUTES_GIVEN = 1468

# Not allowed to update the value of a shard attribute.
CLUSTER_MUST_NOT_CHANGE_SHARDING_ATTRIBUTES = 1469

# Operation not supported in sharded collection.
CLUSTER_UNSUPPORTED = 1470

# Operation is coordinator-only.
CLUSTER_ONLY_ON_COORDINATOR = 1471

# Coordinator or DBServer cannot read the Plan.
CLUSTER_READING_PLAN_AGENCY = 1472

# Coordinator cannot truncate all shards of a cluster collection.
CLUSTER_COULD_NOT_TRUNCATE_COLLECTION = 1473

# Internal communication of the cluster for AQL produces an error.
CLUSTER_AQL_COMMUNICATION = 1474

# Operation is DBServer-only.
CLUSTER_ONLY_ON_DBSERVER = 1477

# Cannot reach a required DBServer.
CLUSTER_BACKEND_UNAVAILABLE = 1478

# Required collection out of sync during AQL execution.
CLUSTER_AQL_COLLECTION_OUT_OF_SYNC = 1481

# Coordinator cannot create an entry for a new index in Plan hierarchy.
CLUSTER_COULD_NOT_CREATE_INDEX_IN_PLAN = 1482

# Coordinator cannot remove an index from Plan hierarchy.
CLUSTER_COULD_NOT_DROP_INDEX_IN_PLAN = 1483

# One tries to create a collection with "shards_like" attribute which points
# to another collection that also has one.
CLUSTER_CHAIN_OF_DISTRIBUTESHARDSLIKE = 1484

# One tries to drop a collection to which another collection points with its
# "shard_like" attribute.
CLUSTER_MUST_NOT_DROP_COLL_OTHER_DISTRIBUTESHARDSLIKE = 1485

# One tries to create a collection which points to an unknown collection in its
# "shard_like" attribute.
CLUSTER_UNKNOWN_DISTRIBUTESHARDSLIKE = 1486

# One tries to create a collection with a "replication_factor" greater than the
# available number of DBServers.
CLUSTER_INSUFFICIENT_DBSERVERS = 1487

# Cannot drop follower.
CLUSTER_COULD_NOT_DROP_FOLLOWER = 1488

# Replication operation refused by a shard leader.
CLUSTER_SHARD_LEADER_REFUSES_REPLICATION = 1489

# Non-replication operation refused by a shard follower.
CLUSTER_SHARD_FOLLOWER_REFUSES_OPERATION = 1490

# Shard leader resigned in the meantime.
CLUSTER_SHARD_LEADER_RESIGNED = 1491

# Agency operation failed after various retries.
CLUSTER_AGENCY_COMMUNICATION_FAILED = 1492

# Servers currently competing for leadership.
CLUSTER_LEADERSHIP_CHALLENGE_ONGOING = 1495

# Operation sent to a non-leading server.
CLUSTER_NOT_LEADER = 1496

# Coordinator cannot create an entry for a new view in Plan hierarchy.
CLUSTER_COULD_NOT_CREATE_VIEW_IN_PLAN = 1497

# Coordinator tries to create a view and the ID already exists.
CLUSTER_VIEW_ID_EXISTS = 1498

# Coordinator cannot drop a collection entry in Plan hierarchy.
CLUSTER_COULD_NOT_DROP_COLLECTION = 1499

#########################
# ArangoDB Query Errors #
#########################

# Running query killed by an explicit admin command.
QUERY_KILLED = 1500

# Parsed query syntactically invalid.
QUERY_PARSE = 1501

# Empty query specified.
QUERY_EMPTY = 1502

# Runtime error caused by query.
QUERY_SCRIPT = 1503

# Number out of range.
QUERY_NUMBER_OUT_OF_RANGE = 1504

# Geo index coordinate invalid or out of range.
QUERY_INVALID_GEO_VALUE = 1505

# Invalid variable name.
QUERY_VARIABLE_NAME_INVALID = 1510

# Variable redeclared in a query.
QUERY_VARIABLE_REDECLARED = 1511

# Variable name unknown or undefined.
QUERY_VARIABLE_NAME_UNKNOWN = 1512

# Cannot acquire lock on collection.
QUERY_COLLECTION_LOCK_FAILED = 1521

# Too many collections or shards in a query.
QUERY_TOO_MANY_COLLECTIONS = 1522

# Document attribute redeclared.
QUERY_DOCUMENT_ATTRIBUTE_REDECLARED = 1530

# Undefined function called.
QUERY_FUNCTION_NAME_UNKNOWN = 1540

# Argument number mismatch.
QUERY_FUNCTION_ARGUMENT_NUMBER_MISMATCH = 1541

# Argument type mismatch.
QUERY_FUNCTION_ARGUMENT_TYPE_MISMATCH = 1542

# Invalid regex.
QUERY_INVALID_REGEX = 1543

# Invalid bind parameters.
QUERY_BIND_PARAMETERS_INVALID = 1550

# Bind parameter missing.
QUERY_BIND_PARAMETER_MISSING = 1551

# Bind parameter undeclared.
QUERY_BIND_PARAMETER_UNDECLARED = 1552

# Invalid bind parameter value or type.
QUERY_BIND_PARAMETER_TYPE = 1553

# Non-boolean value used in logical operation.
QUERY_INVALID_LOGICAL_VALUE = 1560

# Non-numeric value used in arithmetic operation.
QUERY_INVALID_ARITHMETIC_VALUE = 1561

# Divide by zero.
QUERY_DIVISION_BY_ZERO = 1562

# Non-list operand used when expecting an list operand.
QUERY_ARRAY_EXPECTED = 1563

# Function "FAIL()" called inside a query.
QUERY_FAIL_CALLED = 1569

# Geo restriction specified but no suitable geo index found.
QUERY_GEO_INDEX_MISSING = 1570

# Fulltext query performed on a collection without suitable fulltext index.
QUERY_FULLTEXT_INDEX_MISSING = 1571

# Cannot convert value to a date.
QUERY_INVALID_DATE_VALUE = 1572

# Query contains more than one data-modifying operation.
QUERY_MULTI_MODIFY = 1573

# Query contains an invalid aggregate expression.
QUERY_INVALID_AGGREGATE_EXPRESSION = 1574

# Query contains options that cannot be resolved at query compile time.
QUERY_COMPILE_TIME_OPTIONS = 1575

# Query contains an invalid options specification.
QUERY_EXCEPTION_OPTIONS = 1576

# Unusable index hint.
QUERY_FORCED_INDEX_HINT_UNUSABLE = 1577

# Dynamic function not allowed.
QUERY_DISALLOWED_DYNAMIC_CALL = 1578

# Collection data accessed after modification.
QUERY_ACCESS_AFTER_MODIFICATION = 1579

############################
# AQL User Function Errors #
############################

# User function registered with invalid name.
QUERY_FUNCTION_INVALID_NAME = 1580

# User function registered with invalid code.
QUERY_FUNCTION_INVALID_CODE = 1581

# User function not found.
QUERY_FUNCTION_NOT_FOUND = 1582

# Runtime exception raised by query function.
QUERY_FUNCTION_RUNTIME_ERROR = 1583

#############################
# AQL Query Registry Errors #
#############################

# Query received an invalid JSON.
QUERY_BAD_JSON_PLAN = 1590

# Query ID not found.
QUERY_NOT_FOUND = 1591

# User provided expression does not evaluate to true.
QUERY_USER_ASSERT = 1593

# User provided expression does not evaluate to true.
QUERY_USER_WARN = 1594

##########################
# ArangoDB Cursor Errors #
##########################

# Cursor ID not found.
CURSOR_NOT_FOUND = 1600

# Concurrent request still using the cursor.
CURSOR_BUSY = 1601

###############################
# ArangoDB Transaction Errors #
###############################

# Wrong usage of transactions. This is an internal error.
TRANSACTION_INTERNAL = 1650

# Nested transactions.
TRANSACTION_NESTED = 1651

# Unregistered collection used in transaction.
TRANSACTION_UNREGISTERED_COLLECTION = 1652

# Disallowed operation in transaction.
TRANSACTION_DISALLOWED_OPERATION = 1653

# Transaction aborted.
TRANSACTION_ABORTED = 1654

# Transaction not found.
TRANSACTION_NOT_FOUND = 1655

##########################
# User Management Errors #
##########################

# Invalid username.
USER_INVALID_NAME = 1700

# Username already exists.
USER_DUPLICATE = 1702

# User not found.
USER_NOT_FOUND = 1703

# User authenticated by an external server.
USER_EXTERNAL = 1705

######################################
# Service Management Errors (Legacy) #
######################################

# Cannot download service from central repository.
SERVICE_DOWNLOAD_FAILED = 1752

# Service upload from the client to the ArangoDB server failed.
SERVICE_UPLOAD_FAILED = 1753

###############
# LDAP Errors #
###############

# Cannot initialize an LDAP connection.
LDAP_CANNOT_INIT = 1800

# Cannot set an LDAP option.
LDAP_CANNOT_SET_OPTION = 1801

# Cannot bind to an LDAP server.
LDAP_CANNOT_BIND = 1802

# Cannot unbind from an LDAP server.
LDAP_CANNOT_UNBIND = 1803

# Cannot search the LDAP server.
LDAP_CANNOT_SEARCH = 1804

# Cannot start a TLS LDAP session.
LDAP_CANNOT_START_TLS = 1805

# LDAP did not find any objects with the specified search query.
LDAP_FOUND_NO_OBJECTS = 1806

# LDAP found zero or more than one user.
LDAP_NOT_ONE_USER_FOUND = 1807

# LDAP user not identified.
LDAP_USER_NOT_IDENTIFIED = 1808

# Cannot distinguish a valid mode for provided LDAP configuration.
LDAP_INVALID_MODE = 1820

###############
# Task Errors #
###############

# Task created with an invalid ID.
TASK_INVALID_ID = 1850

# Task created with a duplicate ID.
TASK_DUPLICATE_ID = 1851

# Task not found.
TASK_NOT_FOUND = 1852

############################
# Graph / Traversal Errors #
############################

# Invalid name passed to the server.
GRAPH_INVALID_GRAPH = 1901

# Invalid graph name passed to the server.
GRAPH_COULD_NOT_CREATE_GRAPH = 1902

# Invalid vertex ID passed to the server.
GRAPH_INVALID_VERTEX = 1903

# Vertex could not be created.
GRAPH_COULD_NOT_CREATE_VERTEX = 1904

# Vertex could not be changed.
GRAPH_COULD_NOT_CHANGE_VERTEX = 1905

# Invalid edge ID passed to the server.
GRAPH_INVALID_EDGE = 1906

# Edge could not be created.
GRAPH_COULD_NOT_CREATE_EDGE = 1907

# Edge could not be changed.
GRAPH_COULD_NOT_CHANGE_EDGE = 1908

# Too many iterations in graph traversal.
GRAPH_TOO_MANY_ITERATIONS = 1909

# Invalid filter result returned in graph traversal.
GRAPH_INVALID_FILTER_RESULT = 1910

# Edge collection may only be used once in a edge definition.
GRAPH_COLLECTION_MULTI_USE = 1920

# Collection already used by another graph in a different edge definition.
GRAPH_COLLECTION_USE_IN_MULTI_GRAPHS = 1921

# Graph name missing.
GRAPH_CREATE_MISSING_NAME = 1922

# Edge definition malformed (must be a list of dicts).
GRAPH_CREATE_MALFORMED_EDGE_DEFINITION = 1923

# Graph not found.
GRAPH_NOT_FOUND = 1924

# Graph name already exists.
GRAPH_DUPLICATE = 1925

# Vertex collection does not exist or is not part of the graph.
GRAPH_VERTEX_COL_DOES_NOT_EXIST = 1926

# Collection not a vertex collection.
GRAPH_WRONG_COLLECTION_TYPE_VERTEX = 1927

# Vertex collection not in orphan collections of the graph.
GRAPH_NOT_IN_ORPHAN_COLLECTION = 1928

# Collection already used in an edge definition of the graph.
GRAPH_COLLECTION_USED_IN_EDGE_DEF = 1929

# Edge collection not used in any edge definition of the graph.
GRAPH_EDGE_COLLECTION_NOT_USED = 1930

# Collection "_graphs" does not exist.
GRAPH_NO_GRAPH_COLLECTION = 1932

# Invalid example array object string.
GRAPH_INVALID_EXAMPLE_ARRAY_OBJECT_STRING = 1933

# Invalid example type (must be a list or dict).
GRAPH_INVALID_EXAMPLE_ARRAY_OBJECT = 1934

# Invalid number of arguments.
GRAPH_INVALID_NUMBER_OF_ARGUMENTS = 1935

# Invalid parameter type.
GRAPH_INVALID_PARAMETER = 1936

# Invalid ID.
GRAPH_INVALID_ID = 1937

# Collection already in orphans of the graph.
GRAPH_COLLECTION_USED_IN_ORPHANS = 1938

# Edge collection does not exist or is not part of the graph.
GRAPH_EDGE_COL_DOES_NOT_EXIST = 1939

# Graph has no edge collections.
GRAPH_EMPTY = 1940

# Invalid data in "_graphs" collection.
GRAPH_INTERNAL_DATA_CORRUPT = 1941

# Edge collection already defined.
GRAPH_INTERNAL_EDGE_COLLECTION_ALREADY_SET = 1942

# Orphan list argument malformed. Must be a list of strings.
GRAPH_CREATE_MALFORMED_ORPHAN_LIST = 1943

# Collection used as a relation exists.
GRAPH_EDGE_DEFINITION_IS_DOCUMENT = 1944

# Invalid/unknown session ID passed to the server.
SESSION_UNKNOWN = 1950

# Session expired.
SESSION_EXPIRED = 1951

########################
# Simple Client Errors #
########################

# This error should not happen.
SIMPLE_CLIENT_UNKNOWN_ERROR = 2000

# Client could not connect to server.
SIMPLE_CLIENT_COULD_NOT_CONNECT = 2001

# Client could not write data.
SIMPLE_CLIENT_COULD_NOT_WRITE = 2002

# Client could not read data.
SIMPLE_CLIENT_COULD_NOT_READ = 2003

#######################
# Communicator Errors #
#######################

# Communicator request aborted.
COMMUNICATOR_REQUEST_ABORTED = 2100

# Communicator disabled.
COMMUNICATOR_DISABLED = 2101

#######################
# Internal AQL errors #
#######################

# Internal error during AQL execution.
INTERNAL_AQL = 2200

# AQL block wrote in too few output registers.
WROTE_TOO_FEW_OUTPUT_REGISTERS = 2201

# AQL block wrote in too many output registers.
WROTE_TOO_MANY_OUTPUT_REGISTERS = 2202

# AQL block wrote in an output register twice.
WROTE_OUTPUT_REGISTER_TWICE = 2203

# AQL block wrote in a register that is not its output.
WROTE_IN_WRONG_REGISTER = 2204

# AQL block did not copy its input registers.
INPUT_REGISTERS_NOT_COPIED = 2205

##########################
# Foxx Management Errors #
##########################

# Service manifest file not a well-formed JSON.
MALFORMED_MANIFEST_FILE = 3000

# Service manifest contains invalid values.
INVALID_SERVICE_MANIFEST = 3001

# Service folder or bundle does not exist on the server.
SERVICE_FILES_MISSING = 3002

# Local service bundle does not match the checksum in the database.
SERVICE_FILES_OUTDATED = 3003

# Service options contain invalid values.
INVALID_FOXX_OPTIONS = 3004

# Service mountpath contains invalid characters.
INVALID_MOUNTPOINT = 3007

# No service found at given mountpath.
SERVICE_NOT_FOUND = 3009

# Service missing configuration or dependencies.
SERVICE_NEEDS_CONFIGURATION = 3010

# Service already exists at given mountpath.
SERVICE_MOUNTPOINT_CONFLICT = 3011

# Service directory does not contain a manifest file.
SERVICE_MANIFEST_NOT_FOUND = 3012

# Service options are not well-formed JSONs.
SERVICE_OPTIONS_MALFORMED = 3013

# Source path does not match a file or directory.
SERVICE_SOURCE_NOT_FOUND = 3014

# Source path could not be resolved.
SERVICE_SOURCE_ERROR = 3015

# Unknown service script.
SERVICE_UNKNOWN_SCRIPT = 3016

# API for managing Foxx services disabled.
SERVICE_API_DISABLED = 3099

###################################
# JavaScript Module Loader Errors #
###################################

# Cannot resolve module path.
MODULE_NOT_FOUND = 3100

# Module could not be parsed because of a syntax error.
MODULE_SYNTAX_ERROR = 3101

# Failed to invoke the module in its context.
MODULE_FAILURE = 3103

#####################
# Enterprise Errors #
#####################

# Requested collection needs to be smart.
NO_SMART_COLLECTION = 4000

# Given document does not have the smart graph attribute set.
NO_SMART_GRAPH_ATTRIBUTE = 4001

# Smart collection cannot be dropped.
CANNOT_DROP_SMART_COLLECTION = 4002

# "_key" not prefixed with the value of the smart graph attribute.
KEY_MUST_BE_PREFIXED_WITH_SMART_GRAPH_ATTRIBUTE = 4003

# Given smart graph attribute is illegal and cannot be used for sharding.
ILLEGAL_SMART_GRAPH_ATTRIBUTE = 4004

# Smart graph attribute of collection does not match the attribute of graph.
SMART_GRAPH_ATTRIBUTE_MISMATCH = 4005

# Invalid smart join attribute declaration.
INVALID_SMART_JOIN_ATTRIBUTE = 4006

# Key must be prefixed with smart join attribute.
KEY_MUST_BE_PREFIXED_WITH_SMART_JOIN_ATTRIBUTE = 4007

# Document lacks required smart join attribute.
NO_SMART_JOIN_ATTRIBUTE = 4008

# Cannot update the value of the smart join attribute.
CLUSTER_MUST_NOT_CHANGE_SMART_JOIN_ATTRIBUTE = 4009

#########################
# Cluster Repair Errors #
#########################

# General error during cluster repairs.
CLUSTER_REPAIRS_FAILED = 5000

# Cluster repairs not healthy enough.
CLUSTER_REPAIRS_NOT_ENOUGH_HEALTHY = 5001

# Raised on various inconsistencies regarding the replication factor.
CLUSTER_REPAIRS_REPLICATION_FACTOR_VIOLATED = 5002

# Repaired collection has some shards without DBServers.
CLUSTER_REPAIRS_NO_DBSERVERS = 5003

# Shard in collection and its prototype in the corresponding "shard_like"
# collection have mismatching leaders.
CLUSTER_REPAIRS_MISMATCHING_LEADERS = 5004

# Shard in collection and its prototype in the corresponding "shard_like"
# collection don't have the same followers.
CLUSTER_REPAIRS_MISMATCHING_FOLLOWERS = 5005

# Repaired collection does not have "shard_like" as expected.
CLUSTER_REPAIRS_INCONSISTENT_ATTRIBUTES = 5006

# Collection and its "shard_like" prototype have unequal number of DBServers.
CLUSTER_REPAIRS_MISMATCHING_SHARDS = 5007

# Move shard job failed during cluster repairs.
CLUSTER_REPAIRS_JOB_FAILED = 5008

# Move shard job disappeared before finishing.
CLUSTER_REPAIRS_JOB_DISAPPEARED = 5009

# Agency transaction failed during either sending or executing it.
CLUSTER_REPAIRS_OPERATION_FAILED = 5010

#################
# Agency Errors #
#################

# Inform message must be an object.
AGENCY_INFORM_MUST_BE_OBJECT = 20011

# Inform message must contain a uint parameter 'term'.
AGENCY_INFORM_MUST_CONTAIN_TERM = 20012

# Inform message must contain a string parameter 'ID'.
AGENCY_INFORM_MUST_CONTAIN_ID = 20013

# Inform message must contain an array 'active'.
AGENCY_INFORM_MUST_CONTAIN_ACTIVE = 20014

# Inform message must contain an object 'pool'.
AGENCY_INFORM_MUST_CONTAIN_POOL = 20015

# Inform message must contain an object 'min ping'.
AGENCY_INFORM_MUST_CONTAIN_MIN_PING = 20016

# Inform message must contain an object 'max ping'.
AGENCY_INFORM_MUST_CONTAIN_MAX_PING = 20017

# Inform message must contain an object 'timeoutMult'.
AGENCY_INFORM_MUST_CONTAIN_TIMEOUT_MULT = 20018

# Cannot rebuild readDB or the spearHead from replicated log.
AGENCY_CANNOT_REBUILD_DBS = 20021

######################
# Supervision Errors #
######################

# General supervision failure.
SUPERVISION_GENERAL_FAILURE = 20501

#####################
# Dispatcher Errors #
#####################

# Queue is full.
QUEUE_FULL = 21003

######################
# Maintenance Errors #
######################

# Maintenance action cannot be stopped once started.
ACTION_OPERATION_UNABORTABLE = 6002
