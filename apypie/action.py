from __future__ import print_function, absolute_import

from apypie.route import Route
from apypie.example import Example
from apypie.param import Param
from apypie.exceptions import MissingArgumentsError, InvalidArgumentTypesError

try:
    basestring
except NameError:  # Python 3 has no basestring
    basestring = str  # pylint: disable=W0622


class Action:
    """
    Apipie Action
    """

    def __init__(self, name, resource, api):
        self.name = name
        self.resource = resource
        self.api = api

    @property
    def apidoc(self):
        resource_methods = self.api.apidoc['docs']['resources'][self.resource]['methods']
        return [method for method in resource_methods if method['name'] == self.name][0]

    @property
    def routes(self):
        return [Route(route['api_url'], route['http_method'], route['short_description']) for route in self.apidoc['apis']]

    @property
    def params(self):
        return [Param(**param) for param in self.apidoc['params']]

    @property
    def examples(self):
        return [Example.parse(example) for example in self.apidoc['examples']]

    def call(self, params={}, headers={}, options={}):
        return self.api.call(self.resource, self.name, params, headers, options)

    def find_route(self, params=None):
        params = self.filter_empty_params(params)
        sorted_routes = sorted(self.routes, key=lambda route: [-1 * len(route.params_in_path), route.path])
        for route in sorted_routes:
            if sorted(route.params_in_path) == sorted(params.keys()):
                return route
        return sorted_routes[-1]

    def validate(self, values=None):
        self._validate(self.params, values)

    def _add_to_path(self, path=None, *additions):
        if path is None:
            path = ''
        for addition in additions:
            if path == '':
                path = "{}".format(addition)
            else:
                path = "{}[{}]".format(path, addition)
        return path

    def _validate(self, params, values, path=None):
        given_params = set(self.filter_empty_params(values).keys())
        required_params = set([param.name for param in params if param.required])
        missing_params = required_params - given_params
        if missing_params:
            missing_params_with_path = [self._add_to_path(path, param) for param in missing_params]
            message = "The following required parameters are missing: {}".format(', '.join(missing_params_with_path), path)
            raise MissingArgumentsError(message)

        for param, value in values.items():
            param_descriptions = [p for p in params if p.name == param]
            if param_descriptions:
                param_description = param_descriptions[0]
                if param_description.params and value is not None:
                    if param_description.expected_type == 'array':
                        for num, item in enumerate(value):
                            self._validate(param_description.params, item, self._add_to_path(path, param_description.name, num))
                    if param_description.expected_type == 'hash':
                        self._validate(param_description.params, value, self._add_to_path(path, param_description.name))
                if param_description.expected_type == 'boolean':
                    if not isinstance(value, bool) and not (isinstance(value, int) and value in [0, 1]):
                        raise ValueError(param_description.validator)
                if param_description.expected_type == 'numeric':
                    if not isinstance(value, int):
                        raise ValueError(param_description.validator)
                if param_description.expected_type == 'string':
                    if not isinstance(value, basestring):
                        raise ValueError(param_description.validator)

    def filter_empty_params(self, params=None):
        if params is not None:
            if isinstance(params, dict):
                return dict((k, v) for k, v in params.items() if v is not None)
            else:
                raise InvalidArgumentTypesError
        else:
            return {}
