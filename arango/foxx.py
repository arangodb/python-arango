__all__ = ["Foxx"]

import os
from typing import Any, BinaryIO, Dict, Optional, Tuple, Union

from requests_toolbelt import MultipartEncoder

from arango.api import ApiGroup
from arango.exceptions import (
    FoxxCommitError,
    FoxxConfigGetError,
    FoxxConfigReplaceError,
    FoxxConfigUpdateError,
    FoxxDependencyGetError,
    FoxxDependencyReplaceError,
    FoxxDependencyUpdateError,
    FoxxDevModeDisableError,
    FoxxDevModeEnableError,
    FoxxDownloadError,
    FoxxReadmeGetError,
    FoxxScriptListError,
    FoxxScriptRunError,
    FoxxServiceCreateError,
    FoxxServiceDeleteError,
    FoxxServiceGetError,
    FoxxServiceListError,
    FoxxServiceReplaceError,
    FoxxServiceUpdateError,
    FoxxSwaggerGetError,
    FoxxTestRunError,
)
from arango.formatter import format_service_data
from arango.request import Request
from arango.response import Response
from arango.result import Result
from arango.typings import Json, Jsons, Params


class Foxx(ApiGroup):
    """Foxx API wrapper."""

    def __repr__(self) -> str:
        return f"<Foxx in {self._conn.db_name}>"

    def _encode(
        self,
        filename: str,
        config: Optional[Json] = None,
        dependencies: Optional[Json] = None,
    ) -> MultipartEncoder:
        """Encode file, configuration and dependencies into multipart data.

        :param filename: Full path to the javascript file or zip bundle.
        :type filename: str
        :param config: Configuration values.
        :type config: dict | None
        :param dependencies: Dependency settings.
        :type dependencies: dict | None
        :return: Multipart encoder object
        :rtype: requests_toolbelt.MultipartEncoder
        """
        extension = os.path.splitext(filename)[1]
        if extension == ".js":  # pragma: no cover
            source_type = "application/javascript"
        elif extension == ".zip":
            source_type = "application/zip"
        else:
            raise ValueError("File extension must be .zip or .js")

        fields: Dict[str, Union[bytes, Tuple[None, BinaryIO, str]]] = {
            "source": (None, open(filename, "rb"), source_type)
        }

        if config is not None:
            fields["configuration"] = self._conn.serialize(config).encode("utf-8")

        if dependencies is not None:
            fields["dependencies"] = self._conn.serialize(dependencies).encode("utf-8")

        return MultipartEncoder(fields=fields)

    def services(self, exclude_system: bool = False) -> Result[Jsons]:
        """List installed services.

        :param exclude_system: If set to True, system services are excluded.
        :type exclude_system: bool
        :return: List of installed service.
        :rtype: [dict]
        :raise arango.exceptions.FoxxServiceListError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_api/foxx",
            params={"excludeSystem": exclude_system},
        )

        def response_handler(resp: Response) -> Jsons:
            if resp.is_success:
                return [format_service_data(service) for service in resp.body]
            raise FoxxServiceListError(resp, request)

        return self._execute(request, response_handler)

    def service(self, mount: str) -> Result[Json]:
        """Return service metadata.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxServiceGetError: If retrieval fails.
        """
        request = Request(
            method="get", endpoint="/_api/foxx/service", params={"mount": mount}
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxServiceGetError(resp, request)

        return self._execute(request, response_handler)

    def create_service(
        self,
        mount: str,
        source: str,
        config: Optional[Json] = None,
        dependencies: Optional[Json] = None,
        development: Optional[bool] = None,
        setup: Optional[bool] = None,
        legacy: Optional[bool] = None,
    ) -> Result[Json]:
        """Install a new service using JSON definition.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param source: Fully qualified URL or absolute path on the server file
            system. Must be accessible by the server, or by all servers if in
            a cluster.
        :type source: str
        :param config: Configuration values.
        :type config: dict | None
        :param dependencies: Dependency settings.
        :type dependencies: dict | None
        :param development: Enable development mode.
        :type development: bool | None
        :param setup: Run service setup script.
        :type setup: bool | None
        :param legacy: Install the service in 2.8 legacy compatibility mode.
        :type legacy: bool | None
        :return: Service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxServiceCreateError: If install fails.
        """
        params: Params = {"mount": mount}
        if development is not None:
            params["development"] = development
        if setup is not None:
            params["setup"] = setup
        if legacy is not None:
            params["legacy"] = legacy

        data: Json = {"source": source}
        if config is not None:
            data["configuration"] = config
        if dependencies is not None:
            data["dependencies"] = dependencies

        request = Request(
            method="post",
            endpoint="/_api/foxx",
            params=params,
            data=data,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxServiceCreateError(resp, request)

        return self._execute(request, response_handler)

    def create_service_with_file(
        self,
        mount: str,
        filename: str,
        development: Optional[bool] = None,
        setup: Optional[bool] = None,
        legacy: Optional[bool] = None,
        config: Optional[Json] = None,
        dependencies: Optional[Json] = None,
    ) -> Result[Json]:
        """Install a new service using a javascript file or zip bundle.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param filename: Full path to the javascript file or zip bundle.
        :type filename: str
        :param development: Enable development mode.
        :type development: bool | None
        :param setup: Run service setup script.
        :type setup: bool | None
        :param legacy: Install the service in 2.8 legacy compatibility mode.
        :type legacy: bool | None
        :param config: Configuration values.
        :type config: dict | None
        :param dependencies: Dependency settings.
        :type dependencies: dict | None
        :return: Service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxServiceCreateError: If install fails.
        """
        params: Params = {"mount": mount}
        if development is not None:
            params["development"] = development
        if setup is not None:
            params["setup"] = setup
        if legacy is not None:
            params["legacy"] = legacy

        data = self._encode(filename, config, dependencies)
        request = Request(
            method="post",
            endpoint="/_api/foxx",
            params=params,
            data=data,
            headers={"content-type": data.content_type},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxServiceCreateError(resp, request)

        return self._execute(request, response_handler)

    def update_service(
        self,
        mount: str,
        source: str,
        config: Optional[Json] = None,
        dependencies: Optional[Json] = None,
        teardown: Optional[bool] = None,
        setup: Optional[bool] = None,
        legacy: Optional[bool] = None,
        force: Optional[bool] = None,
    ) -> Result[Json]:
        """Update (upgrade) a service.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param source: Fully qualified URL or absolute path on the server file
            system. Must be accessible by the server, or by all servers if in
            a cluster.
        :type source: str
        :param config: Configuration values.
        :type config: dict | None
        :param dependencies: Dependency settings.
        :type dependencies: dict | None
        :param teardown: Run service teardown script.
        :type teardown: bool | None
        :param setup: Run service setup script.
        :type setup: bool | None
        :param legacy: Update the service in 2.8 legacy compatibility mode.
        :type legacy: bool | None
        :param force: Force update if no service is found.
        :type force: bool | None
        :return: Updated service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxServiceUpdateError: If update fails.
        """
        params: Params = {"mount": mount}
        if teardown is not None:
            params["teardown"] = teardown
        if setup is not None:
            params["setup"] = setup
        if legacy is not None:
            params["legacy"] = legacy
        if force is not None:
            params["force"] = force

        data: Json = {}
        if source is not None:
            data["source"] = source
        if config is not None:
            data["configuration"] = config
        if dependencies is not None:
            data["dependencies"] = dependencies

        request = Request(
            method="patch",
            endpoint="/_api/foxx/service",
            params=params,
            data=data,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxServiceUpdateError(resp, request)

        return self._execute(request, response_handler)

    def update_service_with_file(
        self,
        mount: str,
        filename: str,
        teardown: Optional[bool] = None,
        setup: Optional[bool] = None,
        legacy: Optional[bool] = None,
        force: Optional[bool] = None,
        config: Optional[Json] = None,
        dependencies: Optional[Json] = None,
    ) -> Result[Json]:
        """Update (upgrade) a service using a javascript file or zip bundle.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param filename: Full path to the javascript file or zip bundle.
        :type filename: str
        :param teardown: Run service teardown script.
        :type teardown: bool | None
        :param setup: Run service setup script.
        :type setup: bool | None
        :param legacy: Update the service in 2.8 legacy compatibility mode.
        :type legacy: bool | None
        :param force: Force update if no service is found.
        :type force: bool | None
        :param config: Configuration values.
        :type config: dict | None
        :param dependencies: Dependency settings.
        :type dependencies: dict | None
        :return: Updated service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxServiceUpdateError: If update fails.
        """
        params: Params = {"mount": mount}
        if teardown is not None:
            params["teardown"] = teardown
        if setup is not None:
            params["setup"] = setup
        if legacy is not None:
            params["legacy"] = legacy
        if force is not None:
            params["force"] = force

        data = self._encode(filename, config, dependencies)
        request = Request(
            method="patch",
            endpoint="/_api/foxx/service",
            params=params,
            data=data,
            headers={"content-type": data.content_type},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxServiceUpdateError(resp, request)

        return self._execute(request, response_handler)

    def replace_service(
        self,
        mount: str,
        source: str,
        config: Optional[Json] = None,
        dependencies: Optional[Json] = None,
        teardown: Optional[bool] = None,
        setup: Optional[bool] = None,
        legacy: Optional[bool] = None,
        force: Optional[bool] = None,
    ) -> Result[Json]:
        """Replace a service by removing the old one and installing a new one.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param source: Fully qualified URL or absolute path on the server file
            system. Must be accessible by the server, or by all servers if in
            a cluster.
        :type source: str
        :param config: Configuration values.
        :type config: dict | None
        :param dependencies: Dependency settings.
        :type dependencies: dict | None
        :param teardown: Run service teardown script.
        :type teardown: bool | None
        :param setup: Run service setup script.
        :type setup: bool | None
        :param legacy: Replace the service in 2.8 legacy compatibility mode.
        :type legacy: bool | None
        :param force: Force install if no service is found.
        :type force: bool | None
        :return: Replaced service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxServiceReplaceError: If replace fails.
        """
        params: Params = {"mount": mount}
        if teardown is not None:
            params["teardown"] = teardown
        if setup is not None:
            params["setup"] = setup
        if legacy is not None:
            params["legacy"] = legacy
        if force is not None:
            params["force"] = force

        data: Json = {}
        if source is not None:
            data["source"] = source
        if config is not None:
            data["configuration"] = config
        if dependencies is not None:
            data["dependencies"] = dependencies

        request = Request(
            method="put",
            endpoint="/_api/foxx/service",
            params=params,
            data=data,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxServiceReplaceError(resp, request)

        return self._execute(request, response_handler)

    def replace_service_with_file(
        self,
        mount: str,
        filename: str,
        teardown: Optional[bool] = None,
        setup: Optional[bool] = None,
        legacy: Optional[bool] = None,
        force: Optional[bool] = None,
        config: Optional[Json] = None,
        dependencies: Optional[Json] = None,
    ) -> Result[Json]:
        """Replace a service using a javascript file or zip bundle.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param filename: Full path to the javascript file or zip bundle.
        :type filename: str
        :param teardown: Run service teardown script.
        :type teardown: bool | None
        :param setup: Run service setup script.
        :type setup: bool | None
        :param legacy: Replace the service in 2.8 legacy compatibility mode.
        :type legacy: bool | None
        :param force: Force install if no service is found.
        :type force: bool | None
        :param config: Configuration values.
        :type config: dict | None
        :param dependencies: Dependency settings.
        :type dependencies: dict | None
        :return: Replaced service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxServiceReplaceError: If replace fails.
        """
        params: Params = {"mount": mount}
        if teardown is not None:
            params["teardown"] = teardown
        if setup is not None:
            params["setup"] = setup
        if legacy is not None:
            params["legacy"] = legacy
        if force is not None:
            params["force"] = force

        data = self._encode(filename, config, dependencies)
        request = Request(
            method="put",
            endpoint="/_api/foxx/service",
            params=params,
            data=data,
            headers={"content-type": data.content_type},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxServiceReplaceError(resp, request)

        return self._execute(request, response_handler)

    def delete_service(
        self, mount: str, teardown: Optional[bool] = None
    ) -> Result[bool]:
        """Uninstall a service.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param teardown: Run service teardown script.
        :type teardown: bool | None
        :return: True if service was deleted successfully.
        :rtype: bool
        :raise arango.exceptions.FoxxServiceDeleteError: If delete fails.
        """
        params: Params = {"mount": mount}
        if teardown is not None:
            params["teardown"] = teardown

        request = Request(method="delete", endpoint="/_api/foxx/service", params=params)

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise FoxxServiceDeleteError(resp, request)

        return self._execute(request, response_handler)

    def config(self, mount: str) -> Result[Json]:
        """Return service configuration.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Configuration values.
        :rtype: dict
        :raise arango.exceptions.FoxxConfigGetError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_api/foxx/configuration",
            params={"mount": mount},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxConfigGetError(resp, request)

        return self._execute(request, response_handler)

    def update_config(self, mount: str, config: Json) -> Result[Json]:
        """Update service configuration.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param config: Configuration values. Omitted options are ignored.
        :type config: dict
        :return: Updated configuration values.
        :rtype: dict
        :raise arango.exceptions.FoxxConfigUpdateError: If update fails.
        """
        request = Request(
            method="patch",
            endpoint="/_api/foxx/configuration",
            params={"mount": mount},
            data=config,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxConfigUpdateError(resp, request)

        return self._execute(request, response_handler)

    def replace_config(self, mount: str, config: Json) -> Result[Json]:
        """Replace service configuration.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param config: Configuration values. Omitted options are reset to their
            default values or marked as un-configured.
        :type config: dict
        :return: Replaced configuration values.
        :rtype: dict
        :raise arango.exceptions.FoxxConfigReplaceError: If replace fails.
        """
        request = Request(
            method="put",
            endpoint="/_api/foxx/configuration",
            params={"mount": mount},
            data=config,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxConfigReplaceError(resp, request)

        return self._execute(request, response_handler)

    def dependencies(self, mount: str) -> Result[Json]:
        """Return service dependencies.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Dependency settings.
        :rtype: dict
        :raise arango.exceptions.FoxxDependencyGetError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_api/foxx/dependencies",
            params={"mount": mount},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxDependencyGetError(resp, request)

        return self._execute(request, response_handler)

    def update_dependencies(self, mount: str, dependencies: Json) -> Result[Json]:
        """Update service dependencies.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param dependencies: Dependencies settings. Omitted ones are ignored.
        :type dependencies: dict
        :return: Updated dependency settings.
        :rtype: dict
        :raise arango.exceptions.FoxxDependencyUpdateError: If update fails.
        """
        request = Request(
            method="patch",
            endpoint="/_api/foxx/dependencies",
            params={"mount": mount},
            data=dependencies,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxDependencyUpdateError(resp, request)

        return self._execute(request, response_handler)

    def replace_dependencies(self, mount: str, dependencies: Json) -> Result[Json]:
        """Replace service dependencies.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param dependencies: Dependencies settings. Omitted ones are disabled.
        :type dependencies: dict
        :return: Replaced dependency settings.
        :rtype: dict
        :raise arango.exceptions.FoxxDependencyReplaceError: If replace fails.
        """
        request = Request(
            method="put",
            endpoint="/_api/foxx/dependencies",
            params={"mount": mount},
            data=dependencies,
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxDependencyReplaceError(resp, request)

        return self._execute(request, response_handler)

    def enable_development(self, mount: str) -> Result[Json]:
        """Put the service into development mode.

        While the service is running in development mode, it is reloaded from
        the file system, and its setup script (if any) is re-executed every
        time the service handles a request.

        In a cluster with multiple coordinators, changes to the filesystem on
        one coordinator is not reflected across other coordinators.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxDevModeEnableError: If operation fails.
        """
        request = Request(
            method="post",
            endpoint="/_api/foxx/development",
            params={"mount": mount},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxDevModeEnableError(resp, request)

        return self._execute(request, response_handler)

    def disable_development(self, mount: str) -> Result[Json]:
        """Put the service into production mode.

        In a cluster with multiple coordinators, the services on all other
        coordinators are replaced with the version on the calling coordinator.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Service metadata.
        :rtype: dict
        :raise arango.exceptions.FoxxDevModeDisableError: If operation fails.
        """
        request = Request(
            method="delete",
            endpoint="/_api/foxx/development",
            params={"mount": mount},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxDevModeDisableError(resp, request)

        return self._execute(request, response_handler)

    def readme(self, mount: str) -> Result[str]:
        """Return the service readme.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Service readme.
        :rtype: str
        :raise arango.exceptions.FoxxReadmeGetError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_api/foxx/readme",
            params={"mount": mount},
        )

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return resp.raw_body
            raise FoxxReadmeGetError(resp, request)

        return self._execute(request, response_handler)

    def swagger(self, mount: str) -> Result[Json]:
        """Return the Swagger API description for the given service.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Swagger API description.
        :rtype: dict
        :raise arango.exceptions.FoxxSwaggerGetError: If retrieval fails.
        """
        request = Request(
            method="get", endpoint="/_api/foxx/swagger", params={"mount": mount}
        )

        def response_handler(resp: Response) -> Json:
            if not resp.is_success:
                raise FoxxSwaggerGetError(resp, request)

            result: Json = resp.body
            if "basePath" in result:
                result["base_path"] = result.pop("basePath")
            return result

        return self._execute(request, response_handler)

    def download(self, mount: str) -> Result[str]:
        """Download service bundle.

        When development mode is enabled, a new bundle is created every time.
        Otherwise, the bundle represents the version of the service installed
        on the server.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Service bundle in raw string form.
        :rtype: str
        :raise arango.exceptions.FoxxDownloadError: If download fails.
        """
        request = Request(
            method="post", endpoint="/_api/foxx/download", params={"mount": mount}
        )

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return resp.raw_body
            raise FoxxDownloadError(resp, request)

        return self._execute(request, response_handler)

    def commit(self, replace: Optional[bool] = None) -> Result[bool]:
        """Commit local service state of the coordinator to the database.

        This can be used to resolve service conflicts between coordinators
        that cannot be fixed automatically due to missing data.

        :param replace: Overwrite any existing service files in database.
        :type replace: bool | None
        :return: True if the state was committed successfully.
        :rtype: bool
        :raise arango.exceptions.FoxxCommitError: If commit fails.
        """
        params: Params = {}
        if replace is not None:
            params["replace"] = replace

        request = Request(method="post", endpoint="/_api/foxx/commit", params=params)

        def response_handler(resp: Response) -> bool:
            if resp.is_success:
                return True
            raise FoxxCommitError(resp, request)

        return self._execute(request, response_handler)

    def scripts(self, mount: str) -> Result[Json]:
        """List service scripts.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :return: Service scripts.
        :rtype: dict
        :raise arango.exceptions.FoxxScriptListError: If retrieval fails.
        """
        request = Request(
            method="get",
            endpoint="/_api/foxx/scripts",
            params={"mount": mount},
        )

        def response_handler(resp: Response) -> Json:
            if resp.is_success:
                return format_service_data(resp.body)
            raise FoxxScriptListError(resp, request)

        return self._execute(request, response_handler)

    def run_script(self, mount: str, name: str, arg: Any = None) -> Result[Any]:
        """Run a service script.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param name: Script name.
        :type name: str
        :param arg: Arbitrary value passed into the script as first argument.
        :type arg: Any
        :return: Result of the script, if any.
        :rtype: Any
        :raise arango.exceptions.FoxxScriptRunError: If script fails.
        """
        request = Request(
            method="post",
            endpoint=f"/_api/foxx/scripts/{name}",
            params={"mount": mount},
            data=arg,
        )

        def response_handler(resp: Response) -> Any:
            if resp.is_success:
                return resp.body
            raise FoxxScriptRunError(resp, request)

        return self._execute(request, response_handler)

    def run_tests(
        self,
        mount: str,
        reporter: str = "default",
        idiomatic: Optional[bool] = None,
        output_format: Optional[str] = None,
        name_filter: Optional[str] = None,
    ) -> Result[str]:
        """Run service tests.

        :param mount: Service mount path (e.g "/_admin/aardvark").
        :type mount: str
        :param reporter: Test reporter. Allowed values are "default" (simple
            list of test cases), "suite" (object of test cases nested in
            suites), "stream" (raw stream of test results), "xunit" (XUnit or
            JUnit compatible structure), or "tap" (raw TAP compatible stream).
        :type reporter: str
        :param idiomatic: Use matching format for the reporter, regardless of
            the value of parameter **output_format**.
        :type: bool
        :param output_format: Used to further control format. Allowed values
            are "x-ldjson", "xml" and "text". When using "stream" reporter,
            setting this to "x-ldjson" returns newline-delimited JSON stream.
            When using "tap" reporter, setting this to "text" returns plain
            text TAP report. When using "xunit" reporter, settings this to
            "xml" returns an XML instead of JSONML.
        :type output_format: str
        :param name_filter: Only run tests whose full name (test suite and
            test case) matches the given string.
        :type name_filter: str
        :return: Reporter output (e.g. raw JSON string, XML, plain text).
        :rtype: str
        :raise arango.exceptions.FoxxTestRunError: If test fails.
        """
        params: Params = {"mount": mount, "reporter": reporter}
        if idiomatic is not None:
            params["idiomatic"] = idiomatic
        if name_filter is not None:
            params["filter"] = name_filter

        headers = {}
        if output_format == "x-ldjson":
            headers["Accept"] = "application/x-ldjson"
        elif output_format == "xml":
            headers["Accept"] = "application/xml"
        elif output_format == "text":
            headers["Accept"] = "text/plain"

        request = Request(
            method="post", endpoint="/_api/foxx/tests", params=params, headers=headers
        )

        def response_handler(resp: Response) -> str:
            if resp.is_success:
                return resp.raw_body
            raise FoxxTestRunError(resp, request)

        return self._execute(request, response_handler)
