import pytest
import apypie

@pytest.fixture
def api(fixture_dir):
    return apypie.Api((fixture_dir / 'dummy.json').strpath)

def test_init(api):
    assert api
    assert api.apidoc

def test_resources(api):
    expected = ['posts', 'users', 'comments']
    assert expected == api.resources

def test_resource_existing(api):
    resource = api.resource('users')
    assert 'users' == resource.name

def test_resource_missing(api):
    with pytest.raises(IOError) as excinfo:
        api.resource('missing')

def test_resource_actions(api):
    resource = api.resource('users')
    expected = ['index', 'show', 'create', 'update', 'destroy', 'create_unnested']
    assert expected == resource.actions

def test_resource_action(api):
    resource = api.resource('users')
    action = resource.action('show')
    assert 'show' == action.name

def test_resource_action_missing(api):
    with pytest.raises(IOError) as excinfo:
        api.resource('users').action('missing')
