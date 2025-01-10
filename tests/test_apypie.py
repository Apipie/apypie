# pylint: disable=invalid-name,missing-docstring,protected-access
import pytest

import apypie
import requests
import json


def test_init(api):
    assert api
    assert api.apidoc


def test_init_bad_cachedir(tmpdir):
    bad_cachedir = tmpdir.join('bad')
    bad_cachedir.ensure(file=True)
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=bad_cachedir.strpath)
    with pytest.raises(OSError):
        api.apidoc


def test_init_bad_response(requests_mock, tmpdir):
    requests_mock.get('https://api.example.com/apidoc/v1.json', status_code=404)
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath)
    with pytest.raises(apypie.exceptions.DocLoadingError) as excinfo:
        api.apidoc
    assert "Could not load data from https://api.example.com" in str(excinfo.value)


def test_init_with_lang(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.tlh.json', json=data)
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath, language='tlh')
    assert api.apidoc


def test_init_with_missing_lang(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.tlh.json', status_code=404)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath, language='tlh')
    assert api.apidoc


def test_init_with_lang_family(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.tlh_EN.json', status_code=404)
    requests_mock.get('https://api.example.com/apidoc/v1.tlh.json', json=data)
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath, language='tlh_EN')
    assert api.apidoc


def test_init_with_xdg_cachedir(fixture_dir, requests_mock, tmp_xdg_cache_home):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)
    api = apypie.Api(uri='https://api.example.com')
    assert api.apidoc
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(file=1)


def test_init_with_existing_cachedir(fixture_dir, requests_mock, tmp_xdg_cache_home):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)

    json_path = tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'deadc0ffee.json')
    json_path.ensure(file=True)
    fixture_dir.join('dummy.json').copy(json_path)

    api = apypie.Api(uri='https://api.example.com')
    api.apidoc

    assert json_path.check(file=1)
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(exists=0)


def test_init_with_bad_cache(fixture_dir, requests_mock, tmp_xdg_cache_home):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)

    json_path = tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'deadc0ffee.json')
    json_path.ensure(file=True)
    json_path.write('BAD JSON')

    api = apypie.Api(uri='https://api.example.com')
    api.apidoc

    assert json_path.check(file=1)
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(exists=0)


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


@pytest.mark.parametrize('client_cert,client_key,expected', [
    (None, None, None),
    ('client.crt', None, None),
    (None, 'client.key', None),
    ('client.crt', 'client.key', ('client.crt', 'client.key')),
])
def test_init_cert(apidoc_cache_dir, client_cert, client_key, expected):
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=apidoc_cache_dir.strpath,
                     client_cert=client_cert, client_key=client_key)

    assert api._session.cert == expected


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
    api.http_call.assert_called_once_with(api, 'get', '/users', params, headers, None, None)


def test_call_method_and_skip_validation(api, mocker):
    params = {'user': {'vip': True}}
    headers = {'content-type': 'application/json'}
    options = {'skip_validation': True}
    mocker.patch('apypie.Api.http_call', autospec=True)
    api.call('users', 'create', params, headers, options)
    api.http_call.assert_called_once_with(api, 'post', '/users', params, headers, None, None)


def test_call_method_and_fill_params(api, mocker):
    params = {'id': 1}
    headers = {'content-type': 'application/json'}
    mocker.patch('apypie.Api.http_call', autospec=True)
    api.call('users', 'show', params, headers)
    api.http_call.assert_called_once_with(api, 'get', '/users/1', {}, headers, None, None)


def test_http_call_get(api, requests_mock):
    requests_mock.get('https://api.example.com/', text='{}')
    api.http_call('get', '/')


def test_http_call_get_querystring(api, requests_mock):
    requests_mock.get('https://api.example.com/?flag=true', text='{}')
    api.http_call('get', '/', params={'flag': True})


def test_http_call_get_headers(api, requests_mock):
    headers = {'X-Apypie-Test': 'Awesome'}
    expected_headers = {
        'Accept': 'application/json;version=1',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'apypie (https://github.com/Apipie/apypie)',
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


def test_http_call_get_headers_cache(fixture_dir, requests_mock, tmp_xdg_cache_home):
    response_headers = {'Apipie-Checksum': 'c0ffeec0ffee'}
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', headers=response_headers, json=data)

    api = apypie.Api(uri='https://api.example.com')
    api.apidoc

    print(api.apidoc_cache_name)

    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(exists=0)
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'c0ffeec0ffee.json').check(file=1)


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


def test_clean_cache(fixture_dir, requests_mock, tmp_xdg_cache_home):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)
    api = apypie.Api(uri='https://api.example.com')
    assert api.apidoc
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(file=1)
    api.clean_cache()
    assert api._apidoc is None
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(exists=0)


def test_validate_cache(fixture_dir, requests_mock, tmp_xdg_cache_home):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)
    api = apypie.Api(uri='https://api.example.com')
    assert api.apidoc
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(file=1)
    api.validate_cache('testcache')
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(exists=0)
    assert api.apidoc
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'testcache.json').check(file=1)


def test_validate_cache_path_traversal(fixture_dir, requests_mock, tmp_xdg_cache_home):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)
    api = apypie.Api(uri='https://api.example.com')
    assert api.apidoc
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(file=1)
    api.validate_cache('../help/testcache')
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'default.json').check(exists=0)
    assert api.apidoc
    assert tmp_xdg_cache_home.join('apypie', 'https___api.example.com', 'v1', 'testcache.json').check(file=1)


def test_custom_session(fixture_dir, requests_mock, tmpdir):
    headers = {'X-Apypie-Test': 'Custom'}

    my_session = requests.Session()
    my_session.headers = headers

    my_api = apypie.Api(uri='https://api.example.com', session=my_session)

    requests_mock.get('https://api.example.com/', request_headers=headers, text='{}')
    my_api.http_call('get', '/')
