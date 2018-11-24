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

    :param uri: base URL of the server
    :param username: username to access the API
    :param password: username to access the API
    :param api_version: version of the API. Defaults to `1`
    :param language: prefered locale for the API description
    :param apidoc_cache_base_dir: base directory for building apidoc_cache_dir. Defaults to `~/.cache/apipie_bindings`.
    :param apidoc_cache_dir: where to cache the JSON description of the API. Defaults to `apidoc_cache_base_dir/<URI>`.
    :param apidoc_cache_name: name of the cache file. If there is cache in the `apidoc_cache_dir`, it is used. Defaults to `default`.
    :param verify_ssl: should the SSL certificate be verified. Defaults to `True`.

    Usage::

      >>> import apypie
      >>> api = apypie.Api(uri='https://api.example.com', username='admin', password='changeme')
    """

    def __init__(self, **kwargs):
        self.uri = kwargs.get('uri')
        self.api_version = kwargs.get('api_version', 1)
        self.language = kwargs.get('language')
        apidoc_cache_base_dir = kwargs.get('apidoc_cache_base_dir', os.path.join(os.path.expanduser('~/.cache'), 'apypie'))
        self.apidoc_cache_dir = kwargs.get('apidoc_cache_dir', os.path.join(apidoc_cache_base_dir, self.uri.replace(':', '_').replace('/', '_'), 'v{}'.format(self.api_version)))
        self.apidoc_cache_name = kwargs.get('apidoc_cache_name', 'default')

        self._session = requests.Session()
        self._session.verify = kwargs.get('verify_ssl', True)

        self._session.headers = {
            'Accept': 'application/json;version={}'.format(self.api_version)
        }
        if self.language:
            self._session.headers['Accept-Language'] = self.language

        if kwargs.get('username') and kwargs.get('password'):
            self._session.auth = (kwargs['username'], kwargs['password'])

        self.apidoc = self._load_apidoc()

    @property
    def resources(self):
        """List of available resources.

        Usage::

            >>> api.resources
            ['comments', 'users']
        """
        return sorted(self.apidoc['docs']['resources'].keys())

    def resource(self, name):
        """
        Get a resource.

        :param name: the name of the resource to load
        :return: :class:`Resource <Resource>` object
        :rtype: apypie.Resource

        Usage::

            >>> api.resource('users')
        """
        if name in self.resources:
            return Resource(self, name)
        else:
            raise KeyError

    def _load_apidoc(self):
        apifile = os.path.join(self.apidoc_cache_dir, '{}.json'.format(self.apidoc_cache_name))
        try:
            with open(apifile, 'r') as f:
                api_doc = json.load(f)
        except IOError:
            api_doc = self._retrieve_apidoc(apifile)
        return api_doc

    def _retrieve_apidoc(self, apifile):
        try:
            os.makedirs(self.apidoc_cache_dir)
        except OSError as err:
            if err.errno != errno.EEXIST or not os.path.isdir(self.apidoc_cache_dir):
                raise
        try:
            response = self._retrieve_apidoc_call('/apidoc/v{}.json'.format(self.api_version))
        except Exception as e:
            raise DocLoadingError("""Could not load data from {0}: {1}
              - is your server down?
              - was rake apipie:cache run when using apipie cache? (typical production settings)""".format(self.uri, e))
        with open(apifile, 'w') as f:
            f.write(json.dumps(response))
        return response

    def _retrieve_apidoc_call(self, path):
        return self.http_call('get', path)

    def call(self, resource_name, action_name, params={}, headers={}, options={}):
        """
        Call an action in the API.

        It finds most fitting route based on given parameters
        with other attributes necessary to do an API call.

        :param resource_name: name of the resource
        :param action_name: action_name name of the action
        :param params: Dict of parameters to be send in the request
        :param headers: Dict of headers to be send in the request
        :param options: Dict of options to influence the how the call is processed
           * `skip_validation` (Bool) *false* - skip validation of parameters
        :return: :class:`dict` object
        :rtype: dict

        Usage::

            >>> api.call('users', 'show', {'id': 1})
        """
        resource = Resource(self, resource_name)
        action = resource.action(action_name)
        if not options.get('skip_validation', False):
            action.validate(params)

        return self._call_action(action, params, headers, options)

    def _call_action(self, action, params={}, headers={}, options={}):
        route = action.find_route(params)
        get_params = dict((key, value) for key, value in params.items() if key not in route.params_in_path)
        return self.http_call(
            route.method,
            route.path_with_params(params),
            get_params,
            headers, options)

    def http_call(self, http_method, path, params=None, headers=None, options=None):
        full_path = urljoin(self.uri, path)
        kwargs = {}

        if headers:
            kwargs['headers'] = headers

        if params:
            if http_method == 'get':
                kwargs['params'] = params
            else:
                kwargs['json'] = params

        request = self._session.request(http_method, full_path, **kwargs)
        request.raise_for_status()
        return request.json()
