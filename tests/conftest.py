import py.path
import pytest
import apypie


@pytest.fixture
def fixture_dir():
    return py.path.local(__file__).realpath() / '..' / 'fixtures'


@pytest.fixture
def api(fixture_dir):
    return apypie.Api((fixture_dir / 'dummy.json').strpath)


@pytest.fixture
def resource(api):
    return api.resource('users')


@pytest.fixture
def action(resource):
    return resource.action('show')
