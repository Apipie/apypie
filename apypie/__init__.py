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
        return self.apidoc['docs']['resources'].keys()

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
        return [method['name'] for method in self.api.apidoc['docs']['resources'][self.name]['methods']]

    def action(self, name):
        if name in self.actions:
            return Action(self.api, name)
        else:
            raise IOError

class Action:
    """
    Apipie Action
    """
    
    def __init__(self, api, name):
        self.api = api
        self.name = name
