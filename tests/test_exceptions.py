from __future__ import print_function

import pytest
import apypie


def test_docloadingerror(capsys):
    test_message = 'this is DocLoadingError'
    test_error = apypie.exceptions.DocLoadingError(test_message)
    with pytest.raises(apypie.exceptions.DocLoadingError) as e:
        raise test_error
    print(e.value)
    captured = capsys.readouterr()
    assert captured.out == '{}\n'.format(test_message)
