"""
Apypie Action module
"""

from __future__ import print_function, absolute_import

from typing import Optional, Any, Iterable, List, TYPE_CHECKING  # pylint: disable=unused-import  # noqa: F401

from apypie.route import Route
from apypie.example import Example
from apypie.param import Param
from apypie.exceptions import MissingArgumentsError, InvalidArgumentTypesError

if TYPE_CHECKING:
    from apypie.api import Api  # pylint: disable=cyclic-import,unused-import  # noqa: F401


class Action(object):
    """
    Apipie Action
    """

    def __init__(self, name, resource, api):
        # type: (str, str, Api) -> None
        self.name = name
        self.resource = resource
        self.api = api

    @property
    def apidoc(self):
        # type: () -> dict
        """
        The apidoc of this action.

        :returns: The apidoc.
        """

        resource_methods = self.api.apidoc['docs']['resources'][self.resource]['methods']
        return [method for method in resource_methods if method['name'] == self.name][0]

    @property
    def routes(self):
        # type: () -> List[Route]
        """
        The routes this action can be invoked by.

        :returns: The routes
        """

        return [Route(route['api_url'], route['http_method'], route['short_description']) for route in self.apidoc['apis']]

    @property
    def params(self):
        # type: () -> List[Param]
        """
        The params accepted by this action.

        :returns: The params.
        """

        return [Param(**param) for param in self.apidoc['params']]

    @property
    def examples(self):
        # type: () -> List[Example]
        """
        The examples of this action.

        :returns: The examples.
        """

        return [Example.parse(example) for example in self.apidoc['examples']]

    def call(self, params=None, headers=None, options=None, data=None, files=None):  # pylint: disable=too-many-arguments
        # type: (Optional[dict], Optional[dict], Optional[dict], Optional[Any], Optional[dict]) -> Optional[dict]
        """
        Call the API to execute the action.

        :param params: The params that should be passed to the API.
        :param headers: Additional headers to be passed to the API.
        :param options: Options
        :param data: Binary data to be submitted to the API.
        :param files: Files to be submitted to the API.

        :returns: The API response.
        """

        return self.api.call(self.resource, self.name, params, headers, options, data, files)

    def find_route(self, params=None):
        # type: (Optional[dict]) -> Route
        """
        Find the best matching route for a given set of params.

        :param params: Params that should be submitted to the API.

        :returns: The best route.
        """

        param_keys = set(self.filter_empty_params(params).keys())
        sorted_routes = sorted(self.routes, key=lambda route: [-1 * len(route.params_in_path), route.path])
        for route in sorted_routes:
            if set(route.params_in_path) <= param_keys:
                return route
        return sorted_routes[-1]

    def validate(self, values, data=None, files=None):
        # type: (dict, Optional[Any], Optional[dict]) -> None
        """
        Validate a given set of parameter values against the required set of parameters.

        :param values: The values to validate.
        :param data: Additional binary data to validate.
        :param files: Additional files to validate.
        """

        self._validate(self.params, values, data, files)

    @staticmethod
    def _add_to_path(path=None, additions=None):
        # type: (Optional[str], Optional[List[str]]) -> str
        if path is None:
            path = ''
        if additions is None:
            additions = []
        for addition in additions:
            if path == '':
                path = "{}".format(addition)
            else:
                path = "{}[{}]".format(path, addition)
        return path

    def _validate(self, params, values, data=None, files=None, path=None):  # pylint: disable=too-many-arguments,too-many-locals
        # type: (Iterable[Param], dict, Optional[Any], Optional[dict], Optional[str]) -> None
        if not isinstance(values, dict):
            raise InvalidArgumentTypesError
        given_params = set(values.keys())
        given_files = set((files or {}).keys())
        given_data = set((data or {}).keys())
        required_params = {param.name for param in params if param.required}
        missing_params = required_params - given_params - given_files - given_data
        if missing_params:
            missing_params_with_path = [self._add_to_path(path, [param]) for param in missing_params]
            message = "The following required parameters are missing: {}".format(', '.join(missing_params_with_path))
            raise MissingArgumentsError(message)

        for param, value in values.items():
            param_descriptions = [p for p in params if p.name == param]
            if param_descriptions:
                param_description = param_descriptions[0]
                if param_description.params and value is not None:
                    if param_description.expected_type == 'array':
                        for num, item in enumerate(value):
                            self._validate(param_description.params, item, path=self._add_to_path(path, [param_description.name, str(num)]))
                    elif param_description.expected_type == 'hash':
                        self._validate(param_description.params, value, path=self._add_to_path(path, [param_description.name]))
                if (param_description.expected_type == 'numeric' and isinstance(value, str)):
                    try:
                        value = int(value)
                    except ValueError:
                        # this will be caught in the next check
                        pass
                if (not param_description.allow_nil and value is None):
                    raise ValueError("{} can't be {}".format(param, value))
                # pylint: disable=too-many-boolean-expressions
                if (value is not None
                        and ((param_description.expected_type == 'boolean' and not isinstance(value, bool) and not (isinstance(value, int) and value in [0, 1]))
                             or (param_description.expected_type == 'numeric' and not isinstance(value, int))
                             or (param_description.expected_type == 'string' and not isinstance(value, (str, int))))):
                    raise ValueError("{} ({}): {}".format(param, value, param_description.validator))

    @staticmethod
    def filter_empty_params(params=None):
        # type: (Optional[dict]) -> dict
        """
        Filter out any params that have no value.

        :param params: The params to filter.

        :returns: The filtered params.
        """
        result = {}
        if params is not None:
            if isinstance(params, dict):
                result = {k: v for k, v in params.items() if v is not None}
            else:
                raise InvalidArgumentTypesError
        return result

    def prepare_params(self, input_dict):
        # type: (dict) -> dict
        """
        Transform a dict with data into one that can be accepted as params for calling the action.

        This will ignore any keys that are not accepted as params when calling the action.
        It also allows generating nested params without forcing the user to care about them.

        :param input_dict: a dict with data that should be used to fill in the params
        :return: :class:`dict` object
        :rtype: dict

        Usage::

            >>> action.prepare_params({'id': 1})
            {'user': {'id': 1}}
        """
        params = self._prepare_params(self.params, input_dict)
        route_params = self._prepare_route_params(input_dict)
        params.update(route_params)
        return params

    def _prepare_params(self, action_params, input_dict):
        # type: (Iterable[Param], dict) -> dict
        result = {}

        for param in action_params:
            if param.expected_type == 'hash' and param.params:
                nested_dict = input_dict.get(param.name, input_dict)
                nested_result = self._prepare_params(param.params, nested_dict)
                if nested_result:
                    result[param.name] = nested_result
            elif param.name in input_dict:
                result[param.name] = input_dict[param.name]

        return result

    def _prepare_route_params(self, input_dict):
        # type: (dict) -> dict
        result = {}

        route = self.find_route(input_dict)

        for url_param in route.params_in_path:
            if url_param in input_dict:
                result[url_param] = input_dict[url_param]

        return result
