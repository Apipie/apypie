import pytest
import apypie

@pytest.fixture
def api(fixture_dir):
    return apypie.Api((fixture_dir / 'dummy.json').strpath)

@pytest.fixture
def resource(api):
    return api.resource('users')

@pytest.fixture
def action(resource):
    return resource.action('show')

def test_init(api):
    assert api
    assert api.apidoc

def test_resources(api):
    expected = sorted(['posts', 'users', 'comments'])
    assert expected == api.resources

def test_resource_existing(resource):
    assert 'users' == resource.name

def test_resource_missing(api):
    with pytest.raises(IOError):
        api.resource('missing')

def test_resource_actions(resource):
    expected = sorted(['index', 'show', 'create', 'update', 'destroy', 'create_unnested'])
    assert expected == resource.actions

def test_resource_action(action):
    assert 'show' == action.name

def test_resource_action_missing(resource):
    with pytest.raises(IOError):
        resource.action('missing')

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
