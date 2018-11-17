from __future__ import print_function, absolute_import

import json

from apypie.resource import Resource

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
