from __future__ import print_function, absolute_import

import json

class Api:
    """
    Apipie API bindings
    """

    def __init__(self, apifile):
        with open(apifile, 'r') as f:
            self.apidoc = json.load(f)

    @property
    def resources(self):
        return sorted(self.apidoc['docs']['resources'].keys())

    def resource(self, name):
        if name in self.resources:
            return Resource(self, name)
        else:
            raise IOError

class Resource:
    """
    Apipie Resource
    """

    def __init__(self, api, name):
        self.api = api
        self.name = name

    @property
    def actions(self):
        return sorted([method['name'] for method in self.api.apidoc['docs']['resources'][self.name]['methods']])

    def action(self, name):
        if name in self.actions:
            return Action(name, self.name, self.api)
        else:
            raise IOError

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
        return [param for param in self.apidoc['params']]

    @property
    def examples(self):
        return [example for example in self.apidoc['examples']]

class Route:
    """
    Apipie Route
    """

    def __init__(self, path, method, description=""):
        self.path = path
        self.method = method.lower()
        self.description = description
