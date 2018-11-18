def test_resource_action(action):
    assert 'show' == action.name

def test_action_apidoc(action):
    assert action.apidoc

def test_action_routes(action):
    assert action.routes

def test_action_route(action):
    route = action.routes[0]
    assert '/users/:id' == route.path
    assert 'get' == route.method

def test_action_params(resource):
    action = resource.action('create')
    assert action.params

def test_action_examples(resource):
    action = resource.action('index')
    assert action.examples

def test_action_example(resource):
    action = resource.action('index')
    example = action.examples[0]
    assert 'GET' == example.http_method
    assert '/users' == example.path
    assert '' == example.args
    assert 200 == example.status
    assert '[ {"user":{"name":"John Doe" }} ]' in example.response

def test_action_call(resource, mocker):
    params = { }
    headers = { 'content-type': 'application/json' }
    mocker.patch('apypie.Api.call', autospec=True)
    resource.action('index').call(params, headers)
    resource.api.call.assert_called_once_with(resource.api, resource.name, 'index', params, headers, {})
