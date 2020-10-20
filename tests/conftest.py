import json
import os

import py.path
import pytest

import apypie


@pytest.fixture
def fixture_dir():
    return py.path.local(__file__).realpath() / '..' / 'fixtures'


@pytest.fixture
def apidoc_cache_dir(fixture_dir, tmpdir):
    fixture_dir.join('dummy.json').copy(tmpdir / 'default.json')
    fixture_dir.join('dummy.json').copy(tmpdir / 'default.tlh.json')
    return tmpdir


@pytest.fixture
def api(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('dummy.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://api.example.com/apidoc/v1.json', json=data)
    api = apypie.Api(uri='https://api.example.com', apidoc_cache_dir=tmpdir.strpath)
    # explicitly trigger loading of the apidoc
    # our tests often mock Api.http_call, which breaks apidoc loading
    api.apidoc
    return api


@pytest.fixture
def resource(api):
    return api.resource('users')


@pytest.fixture
def action(resource):
    return resource.action('show')


@pytest.fixture
def foreman_api(fixture_dir, requests_mock, tmpdir):
    with fixture_dir.join('foreman.json').open() as read_file:
        data = json.load(read_file)
    requests_mock.get('https://foreman.example.com/apidoc/v2.json', json=data)
    return apypie.Api(uri='https://foreman.example.com', api_version=2, apidoc_cache_dir=tmpdir.strpath)


@pytest.fixture
def preserve_environ():
    old_environ = os.environ.copy()
    try:
        yield
    finally:
        os.environ = old_environ
