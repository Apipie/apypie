import pytest
import apypie

@pytest.fixture
def api(fixture_dir):
    return apypie.Api((fixture_dir / 'dummy.json').strpath)

def test_init(api):
    assert api
    assert api.apidoc

def test_resources(api):
    expected = sorted(['posts', 'users', 'comments'])
    assert expected == api.resources

def test_resource_existing(api):
    resource = api.resource('users')
    assert 'users' == resource.name

def test_resource_missing(api):
    with pytest.raises(IOError):
        api.resource('missing')

def test_resource_actions(api):
    resource = api.resource('users')
    expected = sorted(['index', 'show', 'create', 'update', 'destroy', 'create_unnested'])
    assert expected == resource.actions

def test_resource_action(api):
    resource = api.resource('users')
    action = resource.action('show')
    assert 'show' == action.name

def test_resource_action_missing(api):
    with pytest.raises(IOError):
        api.resource('users').action('missing')

def test_action_apidoc(api):
    resource = api.resource('users')
    action = resource.action('show')
    assert action.apidoc

def test_action_routes(api):
    resource = api.resource('users')
    action = resource.action('show')
    assert action.routes

def test_action_route(api):
    resource = api.resource('users')
    action = resource.action('show')
    route = action.routes[0]
    assert '/users/:id' == route.path
    assert 'get' == route.method

def test_action_params(api):
    resource = api.resource('users')
    action = resource.action('create')
    assert action.params

def test_action_examples(api):
    resource = api.resource('users')
    action = resource.action('index')
    assert action.examples
