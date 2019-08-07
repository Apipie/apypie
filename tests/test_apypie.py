# pylint: disable=invalid-name,missing-docstring,protected-access
import pytest

import apypie
import json
import os


def test_init(api):
    assert api
    assert api.apidoc


def test_init_bad_cachedir(tmpdir):
    bad_cachedir = tmpdir.join('bad')
    bad_cachedir.ensure(file=True)
    with pytest.raises(OSError):
        apypie.Api(uri='https://api.example.com', apidoc_cache_dir=bad_cachedir.strpath)


def test_init_bad_response(requests_mock, tmpdir):
    requests_mock.get('https://api.example.com/apidoc/v1.json', status_code=404)
    with pytest.raises(apypie.exceptions.DocLoadingError) as excinfo:
        apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath)
    assert "Could not load data from https://api.example.com" in str(excinfo.value)


def test_init_with_lang(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.tlh.json', json=data)
    apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath, language='tlh')


def test_init_with_lang_family(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.tlh.json', json=data)
    apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath, language='tlh_EN')


def test_init_with_xdg_cachedir(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)
    old_environ = os.environ.copy()
    os.environ['XDG_CACHE_HOME'] = tmpdir.strpath
    apypie.Api(uri='https://api.example.com')
    os.environ = old_environ
    assert tmpdir.join('apypie/https___api.example.com/v1/default.json').check(file=1)


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
    api.http_call.assert_called_once_with(api, 'get', '/users', params, headers, {}, None)


def test_call_method_and_skip_validation(api, mocker):
    params = {'user': {'vip': True}}
    headers = {'content-type': 'application/json'}
    options = {'skip_validation': True}
    mocker.patch('apypie.Api.http_call', autospec=True)
    api.call('users', 'create', params, headers, options)
    api.http_call.assert_called_once_with(api, 'post', '/users', params, headers, options, None)


def test_call_method_and_fill_params(api, mocker):
    params = {'id': 1}
    headers = {'content-type': 'application/json'}
    mocker.patch('apypie.Api.http_call', autospec=True)
    api.call('users', 'show', params, headers)
    api.http_call.assert_called_once_with(api, 'get', '/users/1', {}, headers, {}, None)


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
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Content-Type': 'application/json',
    }
    requests_mock.post('https://api.example.com/', text='{}', request_headers=expected_headers)
    api.http_call('post', '/')


def test_http_call_post_with_params(api, requests_mock):
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Content-Type': 'application/json',
    }
    params = {'test': 'all the things'}
    requests_mock.post('https://api.example.com/', text='{}', request_headers=expected_headers)
    api.http_call('post', '/', params)


def test_http_call_put(api, requests_mock):
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Content-Type': 'application/json',
    }
    requests_mock.put('https://api.example.com/', text='{}', request_headers=expected_headers)
    api.http_call('put', '/')


def test_http_call_put_with_params(api, requests_mock):
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Content-Type': 'application/json',
    }
    params = {'test': 'all the things'}
    requests_mock.put('https://api.example.com/', text='{}', request_headers=expected_headers)
    api.http_call('put', '/', params)


def test_http_call_delete(api, requests_mock):
    requests_mock.delete('https://api.example.com/', text='{}')
    api.http_call('delete', '/')


def test_http_call_delete_with_params(api, requests_mock):
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Content-Type': 'application/json',
    }
    requests_mock.delete('https://api.example.com/', text='{}', request_headers=expected_headers)
    api.http_call('delete', '/', {'test': 'all the things'})


def test_http_call_with_no_content_answer(api, requests_mock):
    requests_mock.delete('https://api.example.com/', status_code=204)
    api.http_call('delete', '/', {})
