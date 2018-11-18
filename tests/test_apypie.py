def test_init(api):
    assert api
    assert api.apidoc


def test_resources(api):
    expected = sorted(['posts', 'users', 'comments'])
    assert expected == api.resources
