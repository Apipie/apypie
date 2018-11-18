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

    def call(self, resource_name, action_name, params={}, headers={}, options={}):
        resource = Resource(self, resource_name)
        action = resource.action(action_name)
        #action.validate!(params) unless options[:skip_validation]
        #options[:fake_response] = find_match(fake_responses, resource_name, action_name, params) || action.examples.first if dry_run?

        self.call_action(action, params, headers, options)

    def call_action(self, action, params={}, headers={}, options={}):
        route = action.find_route(params)
        return (
            route.method,
            route.path_with_params(params),
            #params.reject { |par, _| route.params_in_path.include? par.to_s },
            headers, options)
