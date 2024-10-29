# pylint: disable=invalid-name,missing-docstring,protected-access
import io
import json

import pytest
import requests
import requests.exceptions

from apypie.foreman import ForemanApi, ForemanApiException, _recursive_dict_keys


def test_recursive_dict_keys():
    a_dict = {'level1': 'has value', 'level2': {'real_level2': 'more value', 'level3': {'real_level3': 'nope'}}}
    expected_keys = set(['level1', 'level2', 'level3', 'real_level2', 'real_level3'])
    assert _recursive_dict_keys(a_dict) == expected_keys


@pytest.fixture
def foremanapi(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('foreman.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v2.json', json=data)
    return ForemanApi(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath)


@pytest.fixture
def lunaapi(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('luna.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v2.json', json=data)
    return ForemanApi(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath)


def test_init(foremanapi):
    assert foremanapi
    assert foremanapi.apidoc


def test_resources(foremanapi):
    assert 'domains' in foremanapi.resources


def test_resource_action(foremanapi, requests_mock):
    requests_mock.get('https://api.example.com/api/organizations/1', json={'id': 1})
    org = foremanapi.resource_action('organizations', 'show', {'id': 1})
    assert org


def test_resource_action_unknown_resource(foremanapi):
    with pytest.raises(ForemanApiException) as excinfo:
        foremanapi.resource_action('bubblegums', 'show', {'id': 1})
    assert "The server doesn't know about bubblegums, is the right plugin installed?" in str(excinfo.value)


def test_resource_action_http_error(foremanapi, mocker):
    raw_bytes = io.BytesIO(b'This is bad')
    response = requests.Response()
    response.raw = raw_bytes
    exception = requests.exceptions.HTTPError(response=response)
    mocker.patch('apypie.foreman.ForemanApi._resource_call', autospec=True, side_effect=exception)
    with pytest.raises(ForemanApiException) as excinfo:
        foremanapi.resource_action('organizations', 'show', {'id': 1})
    assert "Error while performing show on organizations:  - This is bad" in str(excinfo.value)


def test_resource_action_http_error_json(foremanapi, mocker):
    raw_bytes = io.BytesIO(b'{"error":"superbad"}')
    response = requests.Response()
    response.raw = raw_bytes
    exception = requests.exceptions.HTTPError(response=response)
    mocker.patch('apypie.foreman.ForemanApi._resource_call', autospec=True, side_effect=exception)
    with pytest.raises(ForemanApiException) as excinfo:
        foremanapi.resource_action('organizations', 'show', {'id': 1})
    assert "Error while performing show on organizations:  - superbad" in str(excinfo.value)


def test_resource_action_http_error_other_json(foremanapi, mocker):
    raw_bytes = io.BytesIO(b'{"message":"E_TOO_BAD"}')
    response = requests.Response()
    response.raw = raw_bytes
    exception = requests.exceptions.HTTPError(response=response)
    mocker.patch('apypie.foreman.ForemanApi._resource_call', autospec=True, side_effect=exception)
    with pytest.raises(ForemanApiException) as excinfo:
        foremanapi.resource_action('organizations', 'show', {'id': 1})
    assert "Error while performing show on organizations:  - {'message': 'E_TOO_BAD'}" in str(excinfo.value)


def test_resource_action_wait_for_task(lunaapi, requests_mock):
    running_task = {'id': 1, 'state': 'running', 'action': 'test', 'started_at': 'now'}
    stopped_task = {'id': 1, 'state': 'stopped', 'result': 'success'}
    requests_mock.post('https://api.example.com/api/domains', json=running_task)
    requests_mock.get('https://api.example.com/foreman_tasks/api/tasks/1', json=stopped_task)
    done = lunaapi.resource_action('domains', 'create', {'name': 'test'})
    assert done['result'] == 'success'


def test_wait_for_task(lunaapi, requests_mock):
    running_task = {'id': 1, 'state': 'running'}
    stopped_task = {'id': 1, 'state': 'stopped', 'result': 'success'}
    requests_mock.get('https://api.example.com/foreman_tasks/api/tasks/1', json=stopped_task)
    lunaapi.wait_for_task(running_task)


def test_wait_for_task_failed_task(lunaapi, requests_mock):
    running_task = {'id': 1, 'state': 'running'}
    stopped_task = {'id': 1, 'state': 'stopped', 'result': 'error', 'action': 'test', 'humanized': {'errors': 'you lost the game'}}
    requests_mock.get('https://api.example.com/foreman_tasks/api/tasks/1', json=stopped_task)
    with pytest.raises(ForemanApiException) as excinfo:
        lunaapi.wait_for_task(running_task)
    assert "Task test(1) did not succeed. Task information: you lost the game" in str(excinfo.value)


def test_wait_for_task_timeout(lunaapi, requests_mock):
    running_task = {'id': 1, 'state': 'running'}
    requests_mock.get('https://api.example.com/foreman_tasks/api/tasks/1', json=running_task)
    lunaapi.task_timeout = 1
    with pytest.raises(ForemanApiException) as excinfo:
        lunaapi.wait_for_task(running_task)
    assert "Timeout waiting for Task 1" in str(excinfo.value)


def test_show(foremanapi, requests_mock):
    requests_mock.get('https://api.example.com/api/organizations/1', json={'id': 1})
    org = foremanapi.show('organizations', 1)
    assert org


def test_list(foremanapi, requests_mock):
    requests_mock.get('https://api.example.com/api/organizations?per_page=4294967296', complete_qs=True, json={'results': [{'id': 1}]})
    orgs = foremanapi.list('organizations')
    assert orgs


def test_list_with_search(foremanapi, requests_mock):
    requests_mock.get('https://api.example.com/api/organizations?search=name%3DTEST&per_page=4294967296', complete_qs=True, json={'results': [{'id': 1}]})
    orgs = foremanapi.list('organizations', search='name=TEST')
    assert orgs


def test_create(foremanapi, requests_mock):
    def match_json_body(request):
        return {'organization': {'name': 'Test'}} == request.json()

    requests_mock.post('https://api.example.com/api/organizations', additional_matcher=match_json_body, json={'id': 1})
    org = foremanapi.create('organizations', {'name': 'Test'})
    assert org


def test_update(foremanapi, requests_mock):
    def match_json_body(request):
        return {'organization': {'name': 'Test'}} == request.json()

    requests_mock.put('https://api.example.com/api/organizations/1', additional_matcher=match_json_body, json={'id': 1})
    org = foremanapi.update('organizations', {'id': 1, 'name': 'Test'})
    assert org


def test_delete(foremanapi, requests_mock):
    requests_mock.delete('https://api.example.com/api/organizations/1', status_code=204)
    foremanapi.delete('organizations', {'id': 1})


@pytest.mark.parametrize("params,expected", [
    ({'name': 'test'}, ({'organization': {'name': 'test'}}, set())),
    ({'name': 'test', 'nope': 'nope'}, ({'organization': {'name': 'test'}}, {'nope'})),
])
def test_validate_payload(foremanapi, params, expected):
    result = foremanapi.validate_payload('organizations', 'create', params)
    assert result == expected
