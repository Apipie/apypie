from __future__ import print_function, absolute_import

import json
import os
import errno
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
import requests

from apypie.resource import Resource
from apypie.exceptions import DocLoadingError


class Api:
    """
    Apipie API bindings
    """

    def __init__(self, **kwargs):
        self.uri = kwargs.get('uri')
        self.api_version = kwargs.get('api_version', 1)
        self.language = kwargs.get('language')
        apidoc_cache_base_dir = kwargs.get('apidoc_cache_base_dir', os.path.join(os.path.expanduser('~/.cache'), 'apypie'))
        self.apidoc_cache_dir = kwargs.get('apidoc_cache_dir', os.path.join(apidoc_cache_base_dir, self.uri.replace(':', '_').replace('/', '_'), 'v{}'.format(self.api_version)))
        self.apidoc_cache_name = kwargs.get('apidoc_cache_name', 'default')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json;version={}'.format(self.api_version)
        }
        if self.language:
            self.headers['Accept-Language'] = self.language
        self.apidoc = self.load_apidoc()

    @property
    def resources(self):
        return sorted(self.apidoc['docs']['resources'].keys())

    def resource(self, name):
        if name in self.resources:
            return Resource(self, name)
        else:
            raise IOError

    def load_apidoc(self):
        apifile = os.path.join(self.apidoc_cache_dir, '{}.json'.format(self.apidoc_cache_name))
        try:
            with open(apifile, 'r') as f:
                api_doc = json.load(f)
        except IOError:
            api_doc = self.retrieve_apidoc(apifile)
        return api_doc

    def retrieve_apidoc(self, apifile):
        try:
            os.makedirs(self.apidoc_cache_dir)
        except OSError as err:
            if err.errno != errno.EEXIST or not os.path.isdir(self.apidoc_cache_dir):
                raise
        try:
            response = self.retrieve_apidoc_call('/apidoc/v{}.json'.format(self.api_version))
        except Exception as e:
            raise DocLoadingError("""Could not load data from {0}: {1}
              - is your server down?
              - was rake apipie:cache run when using apipie cache? (typical production settings)""".format(self.uri, e))
        with open(apifile, 'w') as f:
            f.write(json.dumps(response))
        return response

    def retrieve_apidoc_call(self, path):
        return self.http_call('get', path)

    def call(self, resource_name, action_name, params={}, headers={}, options={}):
        resource = Resource(self, resource_name)
        action = resource.action(action_name)
        if not options.get('skip_validation', False):
            action.validate(params)

        return self.call_action(action, params, headers, options)

    def call_action(self, action, params={}, headers={}, options={}):
        route = action.find_route(params)
        get_params = dict((key, value) for key, value in params.items() if key not in route.params_in_path)
        return self.http_call(
            route.method,
            route.path_with_params(params),
            get_params,
            headers, options)

    def http_call(self, http_method, path, params=None, headers=None, options=None):
        full_path = urljoin(self.uri, path)
        full_headers = self.headers.copy()
        full_headers.update(headers or {})
        kwargs = {'headers': full_headers}
        if http_method == 'get':
            kwargs['params'] = params or {}
        else:
            kwargs['data'] = params or {}
        if self.username and self.password:
            kwargs['auth'] = (self.username, self.password)
        kwargs['verify'] = self.verify_ssl
        request = requests.request(http_method, full_path, **kwargs)
        request.raise_for_status()
        return request.json()
