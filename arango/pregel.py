from __future__ import absolute_import, unicode_literals

__all__ = ['Pregel']

from arango.api import APIWrapper
from arango.exceptions import (
    PregelJobGetError,
    PregelJobCreateError,
    PregelJobDeleteError
)
from arango.request import Request


class Pregel(APIWrapper):
    """Pregel API wrapper.

    :param connection: HTTP connection.
    :type connection: arango.connection.Connection
    :param executor: API executor.
    :type executor: arango.executor.Executor
    """

    def __init__(self, connection, executor):
        super(Pregel, self).__init__(connection, executor)

    def __repr__(self):
        return '<Pregel in {}>'.format(self._conn.db_name)

    def job(self, job_id):
        """Return the details of a Pregel job.

        :param job_id: Pregel job ID.
        :type job_id: int
        :return: Details of the Pregel job.
        :rtype: dict
        :raise arango.exceptions.PregelJobGetError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/_api/control_pregel/{}'.format(job_id)
        )

        def response_handler(resp):
            if not resp.is_success:
                raise PregelJobGetError(resp, request)
            if 'receivedCount' in resp.body:
                resp.body['received_count'] = resp.body.pop('receivedCount')
            if 'sendCount' in resp.body:
                resp.body['send_count'] = resp.body.pop('sendCount')
            if 'totalRuntime' in resp.body:
                resp.body['total_runtime'] = resp.body.pop('totalRuntime')
            if 'edgeCount' in resp.body:  # pragma: no cover
                resp.body['edge_count'] = resp.body.pop('edgeCount')
            if 'vertexCount' in resp.body:  # pragma: no cover
                resp.body['vertex_count'] = resp.body.pop('vertexCount')
            return resp.body

        return self._execute(request, response_handler)

    def create_job(self,
                   graph,
                   algorithm,
                   store=True,
                   max_gss=None,
                   thread_count=None,
                   async_mode=None,
                   result_field=None,
                   algorithm_params=None):
        """Start a new Pregel job.

        :param graph: Graph name.
        :type graph: str | unicode
        :param algorithm: Algorithm (e.g. "pagerank").
        :type algorithm: str | unicode
        :param store: If set to True, Pregel engine writes results back to the
            database. If set to False, results can be queried via AQL.
        :type store: bool
        :param max_gss: Max number of global iterations for the algorithm.
        :type max_gss: int
        :param thread_count: Number of parallel threads to use per worker.
            This does not influence the number of threads used to load or store
            data from the database (it depends on the number of shards).
        :type thread_count: int
        :param async_mode: If set to True, algorithms which support async mode
            run without synchronized global iterations. This might lead to
            performance increase if there are load imbalances.
        :type async_mode: bool
        :param result_field: If specified, most algorithms will write their
            results into this field.
        :type result_field: str | unicode
        :param algorithm_params: Additional algorithm parameters.
        :type algorithm_params: dict
        :return: Pregel job ID.
        :rtype: int
        :raise arango.exceptions.PregelJobCreateError: If create fails.
        """
        data = {'algorithm': algorithm, 'graphName': graph}

        if algorithm_params is None:
            algorithm_params = {}

        if store is not None:
            algorithm_params['store'] = store
        if max_gss is not None:
            algorithm_params['maxGSS'] = max_gss
        if thread_count is not None:
            algorithm_params['parallelism'] = thread_count
        if async_mode is not None:
            algorithm_params['async'] = async_mode
        if result_field is not None:
            algorithm_params['resultField'] = result_field
        if algorithm_params:
            data['params'] = algorithm_params

        request = Request(
            method='post',
            endpoint='/_api/control_pregel',
            data=data
        )

        def response_handler(resp):
            if resp.is_success:
                return resp.body
            raise PregelJobCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_job(self, job_id):
        """Delete a Pregel job.

        :param job_id: Pregel job ID.
        :type job_id: int
        :return: True if Pregel job was deleted successfully.
        :rtype: bool
        :raise arango.exceptions.PregelJobDeleteError: If delete fails.
        """
        request = Request(
            method='delete',
            endpoint='/_api/control_pregel/{}'.format(job_id)
        )

        def response_handler(resp):
            if resp.is_success:
                return True
            raise PregelJobDeleteError(resp, request)

        return self._execute(request, response_handler)
