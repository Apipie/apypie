import pytest
import apypie

def test_resource_actions(resource):
    expected = sorted(['index', 'show', 'create', 'update', 'destroy', 'create_unnested'])
    assert expected == resource.actions

def test_resource_has_action(resource):
    assert resource.has_action('index')

def test_resource_has_action_false(resource):
    assert not resource.has_action('missing')

def test_resource_action_missing(resource):
    with pytest.raises(IOError):
        resource.action('missing')

def test_resource_action_type(resource):
    assert isinstance(resource.action('index'), apypie.Action)

  # ~ it "should allow user to call the action" do
    # ~ params = { :a => 1 }
    # ~ headers = { :content_type => 'application/json' }
    # ~ ApipieBindings::API.any_instance.expects(:call).with(:users, :index, params, headers, {})
    # ~ resource.call(:index, params, headers)
  # ~ end

  # ~ it "should allow user to call the action with minimal params" do
    # ~ ApipieBindings::API.any_instance.expects(:call).with(:users, :index, {}, {}, {})
    # ~ resource.call(:index)
  # ~ end

def test_resource_existing(resource):
    assert 'users' == resource.name

def test_resource_missing(api):
    with pytest.raises(IOError):
        api.resource('missing')
