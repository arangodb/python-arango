#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

VERSION=3.2.0
NAME=ArangoDB-$VERSION

if [ ! -d "$DIR/$NAME" ]; then
  # download ArangoDB
  echo "curl -L -o $NAME.tar.gz https://www.arangodb.org/repositories/travisCI/$NAME.tar.gz"
  curl -L -o $NAME.tar.gz https://www.arangodb.org/repositories/travisCI/$NAME.tar.gz
  echo "tar zxf $NAME.tar.gz"
  tar zvxf $NAME.tar.gz
fi

ARCH=$(arch)
PID=$(echo $PPID)
TMP_DIR="/tmp/arangodb.$PID"
PID_FILE="/tmp/arangodb.$PID.pid"
ARANGODB_DIR="$DIR/$NAME"
ARANGOD="${ARANGODB_DIR}/bin/arangod_x86_64"

# create database directory
mkdir -p ${TMP_DIR}/agency
mkdir -p ${TMP_DIR}/primary
mkdir -p ${TMP_DIR}/coordinator

echo "Starting ArangoDB Coordinator '${ARANGOD}'"


${ARANGOD} \
    --database.directory ${TMP_DIR}/agency \
    --configuration none \
    --server.endpoint tcp://127.0.0.1:8531 \
    --javascript.app-path ${ARANGODB_DIR}/js/apps \
    --javascript.startup-directory ${ARANGODB_DIR}/js \
    --server.jwt-secret=secret_password \
    --database.maximal-journal-size 1048576 \
    --agency.my-address=tcp://127.0.0.1:8531 \
    --agency.endpoint=tcp://127.0.0.1:8531 \
    --agency.activate=true \
    --agency.size=1 \
    --agency.supervision=true &

${ARANGOD} \
    --database.directory ${TMP_DIR}/primary \
    --configuration none \
    --server.endpoint tcp://127.0.0.1:8530 \
    --javascript.app-path ${ARANGODB_DIR}/js/apps \
    --javascript.startup-directory ${ARANGODB_DIR}/js \
    --server.jwt-secret=secret_password \
    --database.maximal-journal-size 1048576 \
    --cluster.agency-endpoint=tcp://127.0.0.1:8531 \
    --cluster.my-role=PRIMARY \
    --cluster.my-address=tcp://127.0.0.1:8530 &

${ARANGOD} \
    --database.directory ${TMP_DIR}/coordinator \
    --configuration none \
    --server.endpoint tcp://127.0.0.1:8529 \
    --javascript.app-path ${ARANGODB_DIR}/js/apps \
    --javascript.startup-directory ${ARANGODB_DIR}/js \
    --server.jwt-secret=secret_password \
    --database.maximal-journal-size 1048576 \
    --cluster.agency-endpoint=tcp://127.0.0.1:8531 \
    --cluster.my-role=COORDINATOR \
    --cluster.my-address=tcp://127.0.0.1:8529 &

sleep 2

echo "Check for arangod process"
process=$(ps auxww | grep "bin/arangod" | grep -v grep)

if [ "x$process" == "x" ]; then
  echo "no 'arangod' process found"
  echo "ARCH = $ARCH"
  exit 1
fi

echo "Waiting until ArangoDB Coordinator is ready on port 8529"
timeout=120
n=0
while [[ (-z `curl -k --basic --user "root:" -s "http://127.0.0.1:8529/_api/version" `) && (n -lt timeout) ]] ; do
  echo -n "."
  sleep 1s
  n=$[$n+1]
done

if [[ n -eq timeout ]];
then
    echo "Could not start ArangoDB. Timeout reached."
    exit 1
fi

echo "ArangoDB is up"
