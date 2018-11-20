import py.path
import pytest
import apypie


@pytest.fixture
def fixture_dir():
    return py.path.local(__file__).realpath() / '..' / 'fixtures'


@pytest.fixture
def api(fixture_dir):
    return apypie.Api(uri='https://api.example.com', apidoc_cache_dir=fixture_dir.strpath, apidoc_cache_name='dummy')


@pytest.fixture
def resource(api):
    return api.resource('users')


@pytest.fixture
def action(resource):
    return resource.action('show')
