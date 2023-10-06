#!/bin/bash

# Starts a local ArangoDB server or cluster (community or enterprise).
# Useful for testing the python-arango driver against a local ArangoDB setup.

# Usage:
#   ./starter.sh [single|cluster] [community|enterprise] [version]
# Example:
#   ./starter.sh cluster enterprise 3.11.4

setup="${1:-single}"
if [[ "$setup" != "single" && "$setup" != "cluster" ]]; then
    echo "Invalid argument. Please provide either 'single' or 'cluster'."
    exit 1
fi

license="${2:-all}"
if [[ "$license" != "community" && "$license" != "enterprise" ]]; then
    echo "Invalid argument. Please provide either 'community' or 'enterprise'."
    exit 1
fi

version="${3:-3.11.4}"

if [ "$setup" == "single" ]; then
  if [ "$license" == "community" ]; then
    echo "Starting community single server..."
    docker run -d --rm \
      --name arango \
      -p 8528:8528 \
      -p 8529:8529 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/arangodb:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/single.conf"
  elif [ "$license" == "enterprise" ]; then
    echo "Starting enterprise single server..."
    docker run -d --rm \
      --name arango \
      -p 8528:8528 \
      -p 8529:8529 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/enterprise:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/single.conf"
  fi
elif [ "$setup" == "cluster" ]; then
  if [ "$license" == "community" ]; then
    echo "Starting community cluster..."
    docker run -d --rm \
      --name arango \
      -p 8528:8528 \
      -p 8529:8529 \
      -p 8539:8539 \
      -p 8549:8549 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/arangodb:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/cluster.conf"
  elif [ "$license" == "enterprise" ]; then
    echo "Starting enterprise cluster..."
    docker run -d --rm \
      --name arango \
      -p 8528:8528 \
      -p 8529:8529 \
      -p 8539:8539 \
      -p 8549:8549 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/enterprise:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/cluster.conf"
  fi
fi

wget --quiet --waitretry=1 --tries=120 -O - http://localhost:8528/version | jq
if [ $? -eq 0 ]; then
  echo "OK starter ready"
  exit 0
else
  echo "ERROR starter not ready, giving up"
  exit 1
fi
