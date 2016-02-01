from __future__ import absolute_import, unicode_literals

from arango.collections import (
    EdgeCollection,
    VertexCollection
)
from arango.utils import HTTP_OK
from arango.exceptions import *
from arango.request import Request
from arango.api import APIWrapper, api_method


class Graph(APIWrapper):
    """ArangoDB graph.

    A graph can have vertex and edge collections.

    :param connection: ArangoDB connection object
    :type connection: arango.connection.Connection
    :param name: the name of the graph
    :type name: str
    """

    def __init__(self, connection, name):
        self._conn = connection
        self._name = name

    def __repr__(self):
        return "<ArangoDB graph '{}'>".format(self._name)

    @property
    def name(self):
        """Return the name of the graph.

        :returns: the name of the graph
        :rtype: str
        """
        return self._name

    def vertex_collection(self, name):
        """Return the vertex collection object.

        :param name: the name of the vertex collection
        :type name: str
        :returns: the vertex collection object
        :rtype: arango.collections.vertex.VertexCollection
        """
        return VertexCollection(self._conn, self._name, name)

    def edge_collection(self, name):
        """Return the edge collection object.

        :param name: the name of the edge collection
        :type name: str
        :returns: the edge collection object
        :rtype: arango.collections.edge.EdgeCollection
        """
        return EdgeCollection(self._conn, self._name, name)

    @api_method
    def properties(self):
        """Return the graph properties.

        :returns: the graph properties
        :rtype: dict
        :raises arango.exceptions.GraphGetPropertiesError: if the properties
            of the graph cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/gharial/{}'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise GraphGetPropertiesError(res)
            graph = res.body['graph']
            return {
                'id': graph['_id'],
                'name': graph['name'],
                'revision': graph['_rev']
            }
        return request, handler

    ################################
    # Vertex Collection Management #
    ################################

    @api_method
    def orphan_collections(self):
        """Return the orphan vertex collections of the graph.

        :returns: the names of the orphan vertex collections
        :rtype: list
        :raises arango.exceptions.OrphanCollectionsListError: if the list of
            orphan vertex collections cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/gharial/{}'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise OrphanCollectionsListError(res)
            return res.body['graph']['orphanCollections']

        return request, handler

    @api_method
    def vertex_collections(self):
        """Return the vertex collections of the graph.

        :returns: the names of the vertex collections
        :rtype: list
        :raises arango.exceptions.VertexCollectionsListError: if the list of
            vertex collections cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/gharial/{}/vertex'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise VertexCollectionsListError(res)
            return res.body['collections']

        return request, handler

    @api_method
    def create_vertex_collection(self, name):
        """Create a vertex collection for the graph.

        :param name: the name of the new vertex collection to create
        :type name: str
        :returns: the vertex collection object
        :rtype: arango.collections.vertex.VertexCollection
        :raises arango.exceptions.VertexCollectionCreateError: if the vertex
            collection cannot be created
        """
        request = Request(
            method='post',
            endpoint='/_api/gharial/{}/vertex'.format(self._name),
            data={'collection': name}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise VertexCollectionCreateError(res)
            return VertexCollection(self._conn, self._name, name)

        return request, handler

    @api_method
    def delete_vertex_collection(self, name, purge=False):
        """Remove the vertex collection from the graph.

        :param name: the name of the vertex collection to remove
        :type name: str
        :param purge: delete the vertex collection completely
        :type purge: bool
        :returns: whether the operation was successful
        :rtype: bool
        :raises arango.exceptions.VertexCollectionDeleteError: if the vertex
            collection cannot be removed from the graph
        """
        request = Request(
            method='delete',
            endpoint='/_api/gharial/{}/vertex/{}'.format(self._name, name),
            params={'dropCollection': purge}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise VertexCollectionDeleteError(res)
            return not res.body['error']

        return request, handler

    ##############################
    # Edge Definition Management #
    ##############################

    @api_method
    def edge_definitions(self):
        """Return the edge definitions of the graph.

        :returns: the edge definitions of the graph
        :rtype: list
        :raises arango.exceptions.EdgeDefinitionsListError: if the list of
            edge definitions cannot be retrieved
        """
        request = Request(
            method='get',
            endpoint='/_api/gharial/{}'.format(self._name)
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise EdgeDefinitionsListError(res)
            return [
                {
                    'name': edge_definition['collection'],
                    'to_collections': edge_definition['to'],
                    'from_collections': edge_definition['from']
                }
                for edge_definition in
                res.body['graph']['edgeDefinitions']
            ]

        return request, handler

    @api_method
    def create_edge_definition(self, name, from_collections, to_collections):
        """Create a new edge definition for the graph.

        An edge definition consists of an edge collection, one or more "from"
        vertex collections, one or more "to" vertex collections.

        :param name: the name of the new edge collection
        :type name: str
        :param from_collections: the name(s) of the "from" vertex collections
        :type from_collections: list
        :param to_collections: the names of the "to" vertex collections
        :type to_collections: list
        :returns: the edge collection object
        :rtype: arango.collections.edge.EdgeCollection
        :raises arango.exceptions.EdgeDefinitionCreateError: if the edge
            definition cannot be created
        """
        request = Request(
            method='post',
            endpoint='/_api/gharial/{}/edge'.format(self._name),
            data={
                'collection': name,
                'from': from_collections,
                'to': to_collections
            }
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise EdgeDefinitionCreateError(res)
            return EdgeCollection(self._conn, self._name, name)

        return request, handler

    @api_method
    def replace_edge_definition(self, name, from_collections, to_collections):
        """Replace an edge definition in the graph.

        :param name: the name of the edge definition to replace
        :type name: str
        :param from_collections: the names of the "from" vertex collections
        :type from_collections: list
        :param to_collections: the names of the "to" vertex collections
        :type to_collections: list
        :returns: whether the operation was successful
        :rtype: bool
        :raises arango.exceptions.EdgeDefinitionReplaceError: if the edge
            definition cannot be replaced
        """
        request = Request(
            method='put',
            endpoint='/_api/gharial/{}/edge/{}'.format(
                self._name, name
            ),
            data={
                'collection': name,
                'from': from_collections,
                'to': to_collections
            }
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise EdgeDefinitionReplaceError(res)
            return not res.body['error']

        return request, handler

    @api_method
    def delete_edge_definition(self, name, purge=False):
        """Remove an edge definition from the graph.

        :param name: the name of the edge collection
        :type name: str
        :param purge: delete the edge collection completely
        :type purge: bool
        :returns: whether the operation was successful
        :rtype: bool
        :raises arango.exceptions.EdgeDefinitionDeleteError: if the edge
            definition cannot be deleted
        """
        request = Request(
            method='delete',
            endpoint='/_api/gharial/{}/edge/{}'.format(self._name, name),
            params={'dropCollection': purge}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise EdgeDefinitionDeleteError(res)
            return not res.body['error']

        return request, handler

    ####################
    # Graph Traversals #
    ####################

    @api_method
    def traverse(self,
                 start_vertex,
                 direction='outbound',
                 item_order='forward',
                 strategy=None,
                 order=None,
                 edge_uniqueness=None,
                 vertex_uniqueness=None,
                 max_iter=None,
                 min_depth=None,
                 max_depth=None,
                 init_func=None,
                 sort_func=None,
                 filter_func=None,
                 visitor_func=None,
                 expander_func=None):
        """Traverse the graph and return the visited vertices and edges.

        :param start_vertex: the collection and the key of the start vertex in
            the format ``"collection/key"``
        :type start_vertex: str
        :param direction: ``"outbound"`` (default), ``"inbound"`` or ``"any"``
        :type direction: str
        :param item_order: ``"forward"`` (default) or ``"backward"``
        :type item_order: str
        :param strategy: ``"dfs"`` or ``"bfs"``
        :type strategy: str
        :param order: ``"preorder"``, ``"postorder"``, ``"preorder-expander"``
            or ``None`` (default)
        :type order: str
        :param vertex_uniqueness: ``"global"``, ``"path"`` or ``None``
        :type vertex_uniqueness: str
        :param edge_uniqueness: ``"global"``, ``"path"`` or ``None``
        :type edge_uniqueness: str
        :param min_depth: the minimum depth of the nodes to visit
        :type min_depth: int
        :param max_depth: the maximum depth of the nodes to visit
        :type max_depth: int
        :param max_iter: halt the graph traversal after a maximum number of
            iterations (e.g. to prevent endless loops in cyclic graphs)
        :type max_iter: int
        :param init_func: init function in Javascript with signature
            ``(config, result) -> void``, which is used to initialize values
        :type init_func: str
        :param sort_func: sort function in Javascript with signature
            ``(left, right) -> integer``, which returns ``-1`` if ``left <
            right``, ``+1`` if ``left > right``, and ``0`` if ``left == right``
        :type sort_func: str
        :param filter_func: filter function in Javascript with signature
            ``(config, vertex, path) -> mixed``, where mixed can be one of four
            possible values: ``"exclude"`` (do not visit the vertex),
            ``"prune"`` (do not follow the edges of the vertex), ``""`` or
            ``undefined`` (visit the vertex and its edges), or an Array
            (any combinations of the ``"mixed"``, ``"prune"``, ``""`` or
            ``undefined``).
        :type filter_func: str
        :param visitor_func: visitor function in Javascript with signature
            ``(config, result, vertex, path, connected) -> void``, where the
            return value is ignored, ``result`` is modified by reference, and
            ``connected`` is populated only when argument **order** is set to
            ``"preorder-expander"``
        :type visitor_func: str
        :param expander_func: expander function in Javascript with signature
            ``(config, vertex, path) -> mixed``, which must return an array of
            the connections for vertex where each connection is an object with
            attributes edge and vertex
        :type expander_func: str
        :returns: the visited edges and vertices
        :rtype: list
        :raises arango.exceptions.GraphTraverseError: if the graph traversal
            cannot be executed
        """
        if expander_func is None and direction is None:
            direction = 'any'

        if strategy is not None:
            if strategy.lower() == 'dfs':
                strategy = 'depthfirst'
            elif strategy.lower() == 'bfs':
                strategy = 'breadthfirst'

        uniqueness = {}
        if vertex_uniqueness is not None:
            uniqueness['vertices'] = vertex_uniqueness
        if edge_uniqueness is not None:
            uniqueness['edges'] = edge_uniqueness

        data = {
            'startVertex': start_vertex,
            'graphName': self._name,
            'direction': direction,
            'strategy': strategy,
            'order': order,
            'itemOrder': item_order,
            'uniqueness': uniqueness or None,
            'maxIterations': max_iter,
            'minDepth': min_depth,
            'maxDepth': max_depth,
            'init': init_func,
            'filter': filter_func,
            'visitor': visitor_func,
            'sort': sort_func,
            'expander': expander_func
        }
        request = Request(
            method='post',
            endpoint='/_api/traversal',
            data={k: v for k, v in data.items() if v is not None}
        )

        def handler(res):
            if res.status_code not in HTTP_OK:
                raise GraphTraverseError(res)
            return res.body['result']['visited']

        return request, handler
