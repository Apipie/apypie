import apypie


def test_example_apidoc_post():
    example_string = "POST /api/architectures\n{\n  \"architecture\": {\n    \"name\": \"i386\"\n  }\n}\n200\n{\n  \"architecture\": {\n    \"name\": \"i386\",\n    \"id\": 501905020,\n    \"updated_at\": \"2012-12-18T15:24:43Z\",\n    \"operatingsystem_ids\": [],\n    \"created_at\": \"2012-12-18T15:24:43Z\"\n  }\n}"
    example = apypie.Example.parse(example_string)
    assert 'POST' == example.http_method
    assert '/api/architectures' == example.path
    assert '{\n  "architecture": {\n    "name": "i386"\n  }\n}' == example.args
    assert 200 == example.status
    assert '{\n  "architecture": ' in example.response


def test_example_apidoc_get():
    example_string = "GET /api/architectures/x86_64\n200\n{\n  \"architecture\": {\n    \"name\": \"x86_64\",\n    \"id\": 501905019,\n    \"updated_at\": \"2012-12-18T15:24:42Z\",\n    \"operatingsystem_ids\": [\n      309172073,\n      1073012828,\n      331303656\n    ],\n    \"created_at\": \"2012-12-18T15:24:42Z\"\n  }\n}"
    example = apypie.Example.parse(example_string)
    assert 'GET' == example.http_method
    assert '/api/architectures/x86_64' == example.path
    assert '' == example.args
    assert 200 == example.status
    assert '{\n  "architecture": ' in example.response
