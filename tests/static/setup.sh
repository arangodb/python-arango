#!/bin/sh

mkdir -p /tests/static
wget -O /tests/static/service.zip "http://localhost:8000/$PROJECT/tests/static/service.zip"
wget -O /tests/static/keyfile "http://localhost:8000/$PROJECT/tests/static/keyfile"
wget -O /tests/static/arangodb.conf "http://localhost:8000/$PROJECT/tests/static/$ARANGODB_CONF"
arangodb --configuration=/tests/static/arangodb.conf
