#!/bin/bash

# Starts a local ArangoDB server or cluster (community or enterprise).
# Useful for testing the python-arango driver against a local ArangoDB setup.

# Usage:
#   ./starter.sh [single|cluster] [community|enterprise] [version]
# Example:
#   ./starter.sh cluster enterprise 3.11.4

setup="${1:-single}"
license="${2:-community}"
version="${3:-latest}"

extra_ports=""
if [ "$setup" == "single" ]; then
    echo ""
elif [ "$setup" == "cluster" ]; then
    extra_ports="-p 8539:8539 -p 8549:8549"
else
    echo "Invalid argument. Please provide either 'single' or 'cluster'."
    exit 1
fi

image_name=""
if [ "$license" == "community" ]; then
    image_name="arangodb"
elif [ "$license" == "enterprise" ]; then
    image_name="enterprise"
else
    echo "Invalid argument. Please provide either 'community' or 'enterprise'."
    exit 1
fi

if [ "$version" == "latest" ]; then
    conf_file="${setup}-3.12"
else
    conf_file="${setup}-${version%.*}"
fi

docker run -d \
  --name arango \
  -p 8528:8528 \
  -p 8529:8529 \
  $extra_ports \
  -v "$(pwd)/tests/static/":/tests/static \
  -v /tmp:/tmp \
  "arangodb/$image_name:$version" \
  /bin/sh -c "arangodb --configuration=/tests/static/$conf_file.conf"

wget --quiet --waitretry=1 --tries=120 -O - http://localhost:8528/version | jq
if [ $? -eq 0 ]; then
    echo "OK starter ready"
    exit 0
else
    echo "ERROR starter not ready, giving up"
    exit 1
fi
