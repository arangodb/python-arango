"""ArangoDB Database."""

class ArangoDatabase(object):

    def __init__(self, client):
        self._sess = client

    @property
    def version(self):



