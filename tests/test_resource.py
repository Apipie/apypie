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


def test_resource_call_action(resource, mocker):
    params = {}
    headers = {'content-type': 'application/json'}
    mocker.patch('apypie.Api.call', autospec=True)
    resource.call('index', params, headers)
    resource.api.call.assert_called_once_with(resource.api, resource.name, 'index', params, headers, {})


def test_resource_call_action_minimal(resource, mocker):
    mocker.patch('apypie.Api.call', autospec=True)
    resource.call('index')
    resource.api.call.assert_called_once_with(resource.api, resource.name, 'index', {}, {}, {})


def test_resource_existing(resource):
    assert 'users' == resource.name


def test_resource_missing(api):
    with pytest.raises(IOError):
        api.resource('missing')
