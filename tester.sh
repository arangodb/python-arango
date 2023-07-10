#!/bin/bash

# Tests python-arango driver against a local ArangoDB single server or cluster setup.
# 1. Starts a local ArangoDB server or cluster (community).
# 2. Runs the python-arango tests for the community edition.
# 3. Starts a local ArangoDB server or cluster (enterprise).
# 4. Runs all python-arango tests, including enterprise tests.

# Usage:
#   ./tester.sh [all|single|cluster] [all|community|enterprise] [version] ["notest"]

setup="${1:-all}"
if [[ "$setup" != "all" && "$setup" != "single" && "$setup" != "cluster" ]]; then
    echo "Invalid argument. Please provide either 'all', 'single' or 'cluster'."
    exit 1
fi

tests="${2:-all}"
if [[ "$tests" != "all" && "$tests" != "community" && "$tests" != "enterprise" ]]; then
    echo "Invalid argument. Please provide either 'all', 'community', or 'enterprise'."
    exit 1
fi

# 3.11.1
# 3.10.9
# 3.9.9
version="${3:-3.11.1}"

if [[ -n "$4" && "$4" != "notest" ]]; then
    echo "Invalid argument. Use 'notest' to only start the docker container, without running the tests."
    exit 1
fi
mode="${4:-test}"

if [ "$setup" == "all" ] || [ "$setup" == "single" ]; then
  if [ "$tests" == "all" ] || [ "$tests" == "community" ]; then
    echo "Starting single server community setup..."
    docker run -d --rm \
      --name arango \
      -p 8529:8529 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/arangodb:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/single.conf"

    if [[ "$mode" == "notest" ]]; then
      exit 0
    fi

    echo "Running python-arango tests for single server community setup..."
    sleep 3
    py.test --complete --cov=arango --cov-report=html | tee single_community_results.txt
    echo "Stopping single server community setup..."
    docker stop arango
    docker wait arango
    sleep 3
  fi

  if [ "$tests" == "all" ] || [ "$tests" == "enterprise" ]; then
    echo "Starting single server enterprise setup..."
    docker run -d --rm \
      --name arango \
      -p 8529:8529 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/enterprise:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/single.conf"

    if [[ "$mode" == "notest" ]]; then
      exit 0
    fi

    echo "Running python-arango tests for single server enterprise setup..."
    sleep 3
    py.test --complete --enterprise --cov=arango --cov-report=html --cov-append | tee single_enterprise_results.txt
    echo "Stopping single server enterprise setup..."
    docker stop arango
    docker wait arango
    sleep 3
  fi
fi

if [ "$setup" == "all" ] || [ "$setup" == "cluster" ]; then
  if [ "$tests" == "all" ] || [ "$tests" == "community" ]; then
    echo "Starting community cluster setup..."
    docker run -d --rm \
      --name arango \
      -p 8529:8529 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/arangodb:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/cluster.conf"

    if [[ "$mode" == "notest" ]]; then
      exit 0
    fi

    echo "Running python-arango tests for community cluster setup..."
    sleep 15
    py.test --cluster --complete --cov=arango --cov-report=html | tee cluster_community_results.txt
    echo "Stopping community cluster setup..."
    docker stop arango
    docker wait arango
    sleep 3
  fi

  if [ "$tests" == "all" ] || [ "$tests" == "enterprise" ]; then
    echo "Starting enterprise cluster setup..."
    docker run -d --rm \
      --name arango \
      -p 8529:8529 \
      -v "$(pwd)/tests/static/":/tests/static \
      -v /tmp:/tmp \
      arangodb/enterprise:"$version" \
      /bin/sh -c "arangodb --configuration=/tests/static/cluster.conf"

    if [[ "$mode" == "notest" ]]; then
      exit 0
    fi

    echo "Running python-arango tests for enterprise cluster setup..."
    sleep 15
    py.test --cluster --enterprise --complete --cov=arango --cov-report=html | tee cluster_enterprise_results.txt
    echo "Stopping enterprise cluster setup..."
    docker stop arango
    docker wait arango
  fi
fi
