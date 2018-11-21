def test_init(api):
    assert api
    assert api.apidoc


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
        'Content-Type': 'application/json',
        'Accept': 'application/json;version=1'
    }
    expected_headers.update(headers)
    requests_mock.get('https://api.example.com/', request_headers=expected_headers, text='{}')
    api.http_call('get', '/', headers=headers)


def test_http_call_get_with_params(api, requests_mock):
    requests_mock.get('https://api.example.com/?test=all+the+things', text='{}')
    api.http_call('get', '/', {'test': 'all the things'})


def test_http_call_post(api, requests_mock):
    requests_mock.post('https://api.example.com/', text='{}')
    api.http_call('post', '/')


def test_http_call_post_with_params(api, requests_mock):
    params = {'test': 'all the things'}
    requests_mock.post('https://api.example.com/', text='{}')
    api.http_call('post', '/', params)
