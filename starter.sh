#!/bin/bash

# Starts a local ArangoDB server or cluster (community or enterprise).
# Useful for testing the python-arango driver against a local ArangoDB setup.

# Usage:
#   ./starter.sh [single|cluster] [community|enterprise|enterprise-preview] [version]
#   ./starter.sh [single|cluster] [image[:tag]]
# Example:
#   ./starter.sh cluster enterprise 3.12.4
#   ./starter.sh single core-preview 4.0-nightly
#   ./starter.sh single arangodb/enterprise-preview:3.12-nightly

setup="${1:-single}"
image="${2:-community}"
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

image_ref=""
if [[ "$image" == */* ]]; then
    if [[ "$image" == *:* ]]; then
        image_ref="$image"
        if [ "$version" == "latest" ]; then
            version="${image##*:}"
        fi
    else
        image_ref="$image:$version"
    fi
elif [ "$image" == "community" ]; then
    image_ref="arangodb/arangodb:$version"
elif [ "$image" == "enterprise" ]; then
    image_ref="arangodb/enterprise:$version"
elif [ "$image" == "enterprise-preview" ]; then
    image_ref="arangodb/enterprise-preview:$version"
else
    echo "Invalid argument. Please provide 'community', 'enterprise', 'enterprise-preview', or a full image reference."
    exit 1
fi

if [ "$version" == "latest" ]; then
    conf_file="${setup}-3.12"
elif [[ "$version" =~ ^([0-9]+\.[0-9]+) ]]; then
    conf_file="${setup}-${BASH_REMATCH[1]}"
else
    conf_file="${setup}-${version}"
fi

if [ ! -f "tests/static/$conf_file.conf" ]; then
    echo "Missing configuration file: tests/static/$conf_file.conf"
    exit 1
fi

docker run -d \
  --name arango \
  -p 8528:8528 \
  -p 8529:8529 \
  $extra_ports \
  -v "$(pwd)/tests/static/":/tests/static \
  -v /tmp:/tmp \
  "$image_ref" \
  /bin/sh -c "arangodb --configuration=/tests/static/$conf_file.conf"

if [ $? -ne 0 ]; then
    echo "ERROR starter failed to start container"
    exit 1
fi

wget --quiet --waitretry=1 --tries=120 -O - http://localhost:8528/version | jq
if [ $? -eq 0 ]; then
    echo "OK starter ready"
    exit 0
else
    echo "ERROR starter not ready, giving up"
    exit 1
fi
