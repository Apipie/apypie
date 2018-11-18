import pytest
import apypie


@pytest.fixture
def param():
    param = apypie.Param(
        allow_nil=False,
        description="<p>Architecture</p>",
        expected_type="hash",
        full_name="architecture",
        name="architecture",
        params=[
            {
                'allow_nil': False,
                'description': "",
                'expected_type': "string",
                'full_name': "architecture[name]",
                'name': "name",
                'required': False,
                'validator': "Must be String"
            }
        ],
        required=True,
        validator="Must be a Hash"
    )
    return param


def test_param(param):
    assert param


def test_param_nested_params(param):
    assert 'name' == param.params[0].name


def test_param_expected_type(param):
    assert "hash" == param.expected_type


def test_param_description_strip_html(param):
    assert 'Architecture' == param.description


def test_param_required(param):
    assert param.required
    assert not param.params[0].required


def test_param_validator(param):
    assert "Must be a Hash" == param.validator
