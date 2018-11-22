from __future__ import print_function

import pytest
import apypie


def test_printable(capsys):
    test_message = 'this is a printable message'
    printable = apypie.exceptions.Printable()
    printable.message = test_message
    printable.print()
    captured = capsys.readouterr()
    assert captured.out == '{}\n'.format(test_message)


def test_docloadingerror(capsys):
    test_message = 'this is DocLoadingError'
    test_error = apypie.exceptions.DocLoadingError(test_message)
    with pytest.raises(apypie.exceptions.DocLoadingError) as e:
        raise test_error
    assert e.value.message == test_message
    e.value.print()
    captured = capsys.readouterr()
    assert captured.out == '{}\n'.format(test_message)
