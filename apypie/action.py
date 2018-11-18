from __future__ import print_function, absolute_import

from apypie.route import Route
from apypie.example import Example
from apypie.param import Param

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
