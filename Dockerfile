ARG image_name
ARG version

FROM arangodb/${image_name}:${version}
COPY ./tests/static/ /tests/static/
# COPY /tmp /tmp