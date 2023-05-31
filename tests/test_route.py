import pytest
import apypie


@pytest.fixture
def route():
    return apypie.Route("/api/architectures/:id", "GET")


def test_route(route):
    assert route


def test_route_params_in_path(route):
    assert ['id'] == route.params_in_path


def test_route_method_lower(route):
    assert 'get' == route.method


def test_route_path_with_params_fill(route):
    assert '/api/architectures/1' == route.path_with_params({'id': 1})


def test_route_path_with_escaped_params(route):
    assert r'/api/architectures/nested%2Fid' == route.path_with_params({'id': 'nested/id'})


def test_route_path_with_params_fill_wrong(route):
    with pytest.raises(KeyError) as excinfo:
        route.path_with_params({'wrong': 1})
    assert "missing param 'id' in parameters" in str(excinfo.value)


def test_route_path_with_params(route):
    assert '/api/architectures/:id' == route.path_with_params()
