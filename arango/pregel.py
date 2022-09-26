__all__ = ["Pregel"]

from typing import Optional, Sequence

from arango.api import ApiGroup
from arango.exceptions import (
    PregelJobCreateError,
    PregelJobDeleteError,
    PregelJobGetError,
)
from arango.formatter import format_pregel_job_data, format_pregel_job_list
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import Json


class Pregel(ApiGroup):
    """Pregel API wrapper."""

    def __repr__(self) -> str:
        return f"<Pregel in {self._conn.db_name}>"

    def job(self, job_id: int) -> Result[Json]:
        """Return the details of a Pregel job.

        :param job_id: Pregel job ID.
        :type job_id: int
        :return: Details of the Pregel job.
        :rtype: dict
        :raise arango.exceptions.PregelJobGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint=f"/_api/control_pregel/{job_id}")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_pregel_job_data(resp.body)
            raise PregelJobGetError(resp, request)

        return self._execute(request, response_handler)

    def create_job(
        self,
        graph: str,
        algorithm: str,
        store: bool = True,
        max_gss: Optional[int] = None,
        thread_count: Optional[int] = None,
        async_mode: Optional[bool] = None,
        result_field: Optional[str] = None,
        algorithm_params: Optional[Json] = None,
        vertexCollections: Optional[Sequence[str]] = None,
        edgeCollections: Optional[Sequence[str]] = None,
    ) -> Result[int]:
        """Start a new Pregel job.

        :param graph: Graph name.
        :type graph: str
        :param algorithm: Algorithm (e.g. "pagerank").
        :type algorithm: str
        :param store: If set to True, Pregel engine writes results back to the
            database. If set to False, results can be queried via AQL.
        :type store: bool
        :param max_gss: Max number of global iterations for the algorithm.
        :type max_gss: int | None
        :param thread_count: Number of parallel threads to use per worker.
            This does not influence the number of threads used to load or store
            data from the database (it depends on the number of shards).
        :type thread_count: int | None
        :param async_mode: If set to True, algorithms which support async mode
            run without synchronized global iterations. This might lead to
            performance increase if there are load imbalances.
        :type async_mode: bool | None
        :param result_field: If specified, most algorithms will write their
            results into this field.
        :type result_field: str | None
        :param algorithm_params: Additional algorithm parameters.
        :type algorithm_params: dict | None
        :param vertexCollections: List of vertex collection names.
        :type vertexCollections: Sequence[str] | None
        :param edgeCollections: List of edge collection names.
        :type edgeCollections: Sequence[str] | None
        :return: Pregel job ID.
        :rtype: int
        :raise arango.exceptions.PregelJobCreateError: If create fails.
        """
        data: Json = {"algorithm": algorithm, "graphName": graph}

        if vertexCollections is not None:
            data["vertexCollections"] = vertexCollections
        if edgeCollections is not None:
            data["edgeCollections"] = edgeCollections

        if algorithm_params is None:
            algorithm_params = {}

        if store is not None:
            algorithm_params["store"] = store
        if max_gss is not None:
            algorithm_params["maxGSS"] = max_gss
        if thread_count is not None:
            algorithm_params["parallelism"] = thread_count
        if async_mode is not None:
            algorithm_params["async"] = async_mode
        if result_field is not None:
            algorithm_params["resultField"] = result_field
        if algorithm_params:
            data["params"] = algorithm_params

        request = Request(method="post", endpoint="/_api/control_pregel", data=data)

        def response_handler(resp: Response) -> int:
            if resp.is_success:
                return int(resp.body)
            raise PregelJobCreateError(resp, request)

        return self._execute(request, response_handler)

    def delete_job(self, job_id: int) -> Result[bool]:
        """Delete a Pregel job.

        :param job_id: Pregel job ID.
        :type job_id: int
        :return: True if Pregel job was deleted successfully.
        :rtype: bool
        :raise arango.exceptions.PregelJobDeleteError: If delete fails.
        """
        request = Request(method="delete", endpoint=f"/_api/control_pregel/{job_id}")

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise PregelJobDeleteError(resp, request)

        return self._execute(request, response_handler)

    def jobs(self) -> Result[Json]:
        """Returns a list of currently running and recently
            finished Pregel jobs without retrieving their results.

        :return: Details of each running or recently finished Pregel job.
        :rtype: dict
        :raise arango.exceptions.PregelJobGetError: If retrieval fails.
        """
        request = Request(method="get", endpoint="/_api/control_pregel")

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_pregel_job_list(resp.body)
            raise PregelJobGetError(resp, request)

        return self._execute(request, response_handler)
