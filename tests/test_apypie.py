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
