# pylint: disable=invalid-name,missing-docstring,protected-access
import pytest

import apypie


def test_init(api):
    assert api
    assert api.apidoc


@pytest.mark.parametrize('username,password,expected', [
    (None, None, None),
    ('user', None, None),
    (None, 'pass', None),
    ('user', 'pass', ('user', 'pass')),
])
def test_init_auth(apidoc_cache_dir, username, password, expected):
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=apidoc_cache_dir.strpath,
                     username=username, password=password)

    assert api._session.auth == expected


def test_init_language(apidoc_cache_dir):
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=apidoc_cache_dir.strpath,
                     language='tlh')

    assert api.language == 'tlh'
    assert api._session.headers['Accept-Language'] == 'tlh'


def test_resources(api):
    expected = sorted(['posts', 'users', 'comments'])
    assert expected == api.resources


def test_call_method(api, mocker):
    params = {'a': 1}
    headers = {'content-type': 'application/json'}
    mocker.patch('apypie.Api.http_call', autospec=True)
    api.call('users', 'index', params, headers)
    api.http_call.assert_called_once_with(api, 'get', '/users', params, headers, {})


def test_call_method_and_skip_validation(api, mocker):
    params = {'user': {'vip': True}}
    headers = {'content-type': 'application/json'}
    options = {'skip_validation': True}
    mocker.patch('apypie.Api.http_call', autospec=True)
    api.call('users', 'create', params, headers, options)
    api.http_call.assert_called_once_with(api, 'post', '/users', params, headers, options)


def test_call_method_and_fill_params(api, mocker):
    params = {'id': 1}
    headers = {'content-type': 'application/json'}
    mocker.patch('apypie.Api.http_call', autospec=True)
    api.call('users', 'show', params, headers)
    api.http_call.assert_called_once_with(api, 'get', '/users/1', {}, headers, {})


def test_http_call_get(api, requests_mock):
    requests_mock.get('https://api.example.com/', text='{}')
    api.http_call('get', '/')


def test_http_call_get_headers(api, requests_mock):
    headers = {'X-Apypie-Test': 'Awesome'}
    expected_headers = {
        'Accept': 'application/json;version=1',
    }
    expected_headers.update(headers)
    requests_mock.get('https://api.example.com/', request_headers=expected_headers, text='{}')
    api.http_call('get', '/', headers=headers)


def test_http_call_get_headers_auth(apidoc_cache_dir, requests_mock):
    headers = {'X-Apypie-Test': 'Awesome'}
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Authorization': 'Basic dXNlcjpwYXNz',
    }
    expected_headers.update(headers)
    requests_mock.get('https://api.example.com/', request_headers=expected_headers, text='{}')
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=apidoc_cache_dir.strpath,
                     username='user', password='pass')
    api.http_call('get', '/', headers=headers)


def test_http_call_get_headers_auth_lang(apidoc_cache_dir, requests_mock):
    headers = {'X-Apypie-Test': 'Awesome'}
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Accept-Language': 'tlh',
        'Authorization': 'Basic dXNlcjpwYXNz',
    }
    expected_headers.update(headers)
    requests_mock.get('https://api.example.com/', request_headers=expected_headers, text='{}')
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=apidoc_cache_dir.strpath,
                     username='user', password='pass', language='tlh')
    api.http_call('get', '/', headers=headers)


def test_http_call_get_headers_lang(apidoc_cache_dir, requests_mock):
    headers = {'X-Apypie-Test': 'Awesome'}
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Accept-Language': 'tlh',
    }
    expected_headers.update(headers)
    requests_mock.get('https://api.example.com/', request_headers=expected_headers, text='{}')
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=apidoc_cache_dir.strpath,
                     language='tlh')
    api.http_call('get', '/', headers=headers)


def test_http_call_get_with_params(api, requests_mock):
    requests_mock.get('https://api.example.com/?test=all+the+things', text='{}')
    api.http_call('get', '/', {'test': 'all the things'})


def test_http_call_post(api, requests_mock):
    requests_mock.post('https://api.example.com/', text='{}')
    api.http_call('post', '/')


def test_http_call_post_with_params(api, requests_mock):
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Content-Type': 'application/json',
    }
    params = {'test': 'all the things'}
    requests_mock.post('https://api.example.com/', text='{}', headers=expected_headers)
    api.http_call('post', '/', params)
