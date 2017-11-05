#!/bin/bash

which -s brew
if [[ $? != 0 ]] ; then
    echo "Homebrew is required to run this script."
    exit 1
fi

if brew ls --versions arangodb > /dev/null; then
  echo "ArangoDB already installed."
else
  brew install arangodb
fi

PID=$(echo $PPID)
TMP_DIR="/tmp/arangodb.$PID"
PID_FILE="/tmp/arangodb.$PID.pid"
ARANGODB_DIR="/usr/local/opt/arangodb"
ARANGOD="${ARANGODB_DIR}/sbin/arangod"

echo "Creating temporary database directory ..."
mkdir ${TMP_DIR}

echo "Starting ArangoDB '${ARANGOD}' ..."
${ARANGOD} \
    --database.directory ${TMP_DIR} \
    --configuration none \
    --server.endpoint tcp://127.0.0.1:8529 \
    --javascript.app-path ${ARANGODB_DIR}/share/arangodb3/js/apps \
    --javascript.startup-directory ${ARANGODB_DIR}/share/arangodb3/js \
    --database.maximal-journal-size 1048576 &
sleep 2

echo "Checking for 'arangod' process ..."
process=$(ps auxww | grep "bin/arangod" | grep -v grep)
if [ "x$process" == "x" ]; then
  echo "No 'arangod' process found"
  exit 1
fi

echo "Waiting until ArangoDB is ready on port 8529 ..."
sleep 10

echo "ArangoDB is up!"
