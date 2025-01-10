"""
Apypie Api module
"""

from __future__ import print_function, absolute_import

import errno
import glob
import json
from json.decoder import JSONDecodeError  # type: ignore
import os
from urllib.parse import urljoin  # type: ignore
import requests

from apypie.resource import Resource
from apypie.exceptions import DocLoadingError

from typing import Any, Iterable, Optional, TYPE_CHECKING  # pylint: disable=unused-import  # noqa: F401

if TYPE_CHECKING:
    from apypie.action import Action  # pylint: disable=unused-import  # noqa: F401


NO_CONTENT = 204


def _qs_param(param):
    # type: (Any) -> Any
    if isinstance(param, bool):
        return str(param).lower()
    return param


class Api(object):
    """
    Apipie API bindings

    :param uri: base URL of the server
    :param username: username to access the API
    :param password: password to access the API
    :param client_cert: client cert to access the API
    :param client_key: client key to access the API
    :param api_version: version of the API. Defaults to `1`
    :param language: prefered locale for the API description
    :param apidoc_cache_base_dir: base directory for building apidoc_cache_dir. Defaults to `~/.cache/apipie_bindings`.
    :param apidoc_cache_dir: where to cache the JSON description of the API. Defaults to `apidoc_cache_base_dir/<URI>`.
    :param apidoc_cache_name: name of the cache file. If there is cache in the `apidoc_cache_dir`, it is used. Defaults to `default`.
    :param verify_ssl: should the SSL certificate be verified. Defaults to `True`.
    :param session: a `requests.Session` compatible object. Defaults to `requests.Session()`.

    Usage::

      >>> import apypie
      >>> api = apypie.Api(uri='https://api.example.com', username='admin', password='changeme')
    """

    def __init__(self, **kwargs):
        self.uri = kwargs.get('uri')
        self.api_version = kwargs.get('api_version', 1)
        self.language = kwargs.get('language')

        # Find where to put the cache by default according to the XDG spec
        # Not using just get('XDG_CACHE_HOME', '~/.cache') because the spec says
        # that the defaut should be used if "$XDG_CACHE_HOME is either not set or empty"
        xdg_cache_home = os.environ.get('XDG_CACHE_HOME', None)
        if not xdg_cache_home:
            xdg_cache_home = '~/.cache'

        apidoc_cache_base_dir = kwargs.get('apidoc_cache_base_dir', os.path.join(os.path.expanduser(xdg_cache_home), 'apypie'))
        apidoc_cache_dir_default = os.path.join(apidoc_cache_base_dir, self.uri.replace(':', '_').replace('/', '_'), 'v{}'.format(self.api_version))
        self.apidoc_cache_dir = kwargs.get('apidoc_cache_dir', apidoc_cache_dir_default)
        self.apidoc_cache_name = kwargs.get('apidoc_cache_name', self._find_cache_name())

        self._session = kwargs.get('session') or requests.Session()
        self._session.verify = kwargs.get('verify_ssl', True)

        self._session.headers['Accept'] = 'application/json;version={}'.format(self.api_version)
        self._session.headers['User-Agent'] = 'apypie (https://github.com/Apipie/apypie)'
        if self.language:
            self._session.headers['Accept-Language'] = self.language

        if kwargs.get('username') and kwargs.get('password'):
            self._session.auth = (kwargs['username'], kwargs['password'])

        if kwargs.get('client_cert') and kwargs.get('client_key'):
            self._session.cert = (kwargs['client_cert'], kwargs['client_key'])

        self._apidoc = None

    @property
    def apidoc(self):
        # type: () -> dict
        """
        The full apidoc.

        The apidoc will be fetched from the server, if that didn't happen yet.

        :returns: The apidoc.
        """

        if self._apidoc is None:
            self._apidoc = self._load_apidoc()
        return self._apidoc

    @property
    def apidoc_cache_file(self):
        # type: () -> str
        """
        Full local path to the cached apidoc.
        """

        return os.path.join(self.apidoc_cache_dir, '{0}{1}'.format(self.apidoc_cache_name, self.cache_extension))

    def _cache_dir_contents(self):
        # type: () -> Iterable[str]
        return glob.iglob(os.path.join(self.apidoc_cache_dir, '*{}'.format(self.cache_extension)))

    def _find_cache_name(self, default='default'):
        cache_file = next(self._cache_dir_contents(), None)
        cache_name = default
        if cache_file:
            cache_name = os.path.basename(cache_file)[:-len(self.cache_extension)]
        return cache_name

    def validate_cache(self, cache_name=None):
        # type: (Optional[str]) -> None
        """
        Ensure the cached apidoc matches the one presented by the server.

        :param cache_name: The name of the apidoc on the server.
        """

        if cache_name is not None and cache_name != self.apidoc_cache_name:
            self.clean_cache()
            self.apidoc_cache_name = os.path.basename(os.path.normpath(cache_name))

    def clean_cache(self):
        # type: () -> None
        """
        Remove any locally cached apidocs.
        """

        self._apidoc = None
        for filename in self._cache_dir_contents():
            os.unlink(filename)

    @property
    def resources(self):
        # type: () -> Iterable
        """
        List of available resources.

        Usage::

            >>> api.resources
            ['comments', 'users']
        """
        return sorted(self.apidoc['docs']['resources'].keys())

    def resource(self, name):
        # type: (str) -> Resource
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
        message = "Resource '{}' does not exist in the API. Existing resources: {}".format(name, ', '.join(sorted(self.resources)))
        raise KeyError(message)

    def _load_apidoc(self):
        # type: () -> dict
        try:
            with open(self.apidoc_cache_file, 'r') as apidoc_file:  # pylint:disable=all
                api_doc = json.load(apidoc_file)
        except (IOError, JSONDecodeError):
            api_doc = self._retrieve_apidoc()
        return api_doc

    def _retrieve_apidoc(self):
        # type: () -> dict
        try:
            os.makedirs(self.apidoc_cache_dir)
        except OSError as err:
            if err.errno != errno.EEXIST or not os.path.isdir(self.apidoc_cache_dir):
                raise
        response = None
        if self.language:
            response = self._retrieve_apidoc_call('/apidoc/v{0}.{1}.json'.format(self.api_version, self.language), safe=True)
            language_family = self.language.split('_')[0]
            if not response and language_family != self.language:
                response = self._retrieve_apidoc_call('/apidoc/v{0}.{1}.json'.format(self.api_version, language_family), safe=True)
        if not response:
            try:
                response = self._retrieve_apidoc_call('/apidoc/v{}.json'.format(self.api_version))
            except Exception as exc:
                raise DocLoadingError("""Could not load data from {0}: {1}
                  - is your server down?""".format(self.uri, exc))
        if not response:
            raise DocLoadingError("""Could not load data from {0}""".format(self.uri))
        with open(self.apidoc_cache_file, 'w') as apidoc_file:  # pylint:disable=all
            apidoc_file.write(json.dumps(response))
        return response

    def _retrieve_apidoc_call(self, path, safe=False):
        # type: (str, bool) -> Optional[dict]
        try:
            return self.http_call('get', path)
        except Exception:
            if not safe:
                raise
            return None

    def call(self, resource_name, action_name, params=None, headers=None, options=None, data=None, files=None):  # pylint: disable=too-many-arguments
        # type: (str, str, Optional[dict], Optional[dict], Optional[dict], Optional[dict], Optional[dict]) -> Optional[dict]
        """
        Call an action in the API.

        It finds most fitting route based on given parameters
        with other attributes necessary to do an API call.

        :param resource_name: name of the resource
        :param action_name: action_name name of the action
        :param params: Dict of parameters to be sent in the request
        :param headers: Dict of headers to be sent in the request
        :param options: Dict of options to influence the how the call is processed
           * `skip_validation` (Bool) *false* - skip validation of parameters
        :param data: Binary data to be sent in the request
        :param files: Binary files to be sent in the request
        :return: :class:`dict` object
        :rtype: dict

        Usage::

            >>> api.call('users', 'show', {'id': 1})
        """
        if options is None:
            options = {}
        if params is None:
            params = {}

        resource = Resource(self, resource_name)
        action = resource.action(action_name)
        if not options.get('skip_validation', False):
            action.validate(params, data, files)

        return self._call_action(action, params, headers, data, files)

    def _call_action(self, action, params=None, headers=None, data=None, files=None):  # pylint: disable=too-many-arguments
        # type: (Action, Optional[dict], Optional[dict], Optional[dict], Optional[dict]) -> Optional[dict]
        if params is None:
            params = {}

        route = action.find_route(params)
        get_params = {key: value for key, value in params.items() if key not in route.params_in_path}
        return self.http_call(
            route.method,
            route.path_with_params(params),
            get_params,
            headers, data, files)

    def http_call(self, http_method, path, params=None, headers=None, data=None, files=None):  # pylint: disable=too-many-arguments
        # type: (str, str, Optional[dict], Optional[dict], Optional[dict], Optional[dict]) -> Optional[dict]
        """
        Execute an HTTP request.

        :param params: Dict of parameters to be sent in the request
        :param headers: Dict of headers to be sent in the request
        :param data: Binary data to be sent in the request
        :param files: Binary files to be sent in the request

        :return: :class:`dict` object
        :rtype: dict
        """

        full_path = urljoin(self.uri, path)
        kwargs = {
            'verify': self._session.verify,
        }

        if headers:
            kwargs['headers'] = headers

        if params:
            if http_method in ['get', 'head']:
                kwargs['params'] = {k: _qs_param(v) for k, v in params.items()}
            else:
                kwargs['json'] = params
        elif http_method in ['post', 'put', 'patch'] and not data and not files:
            kwargs['json'] = {}

        if files:
            kwargs['files'] = files

        if data:
            kwargs['data'] = data

        request = self._session.request(http_method, full_path, **kwargs)
        request.raise_for_status()
        self.validate_cache(request.headers.get('apipie-checksum'))
        if request.status_code == NO_CONTENT:
            return None
        return request.json()

    @property
    def cache_extension(self):
        # type: () -> str
        """
        File extension for the local cache file.

        Will include the language if set.
        """

        if self.language:
            ext = '.{}.json'.format(self.language)
        else:
            ext = '.json'
        return ext
