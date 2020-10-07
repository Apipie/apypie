"""
Apypie Exceptions
"""

from __future__ import print_function, absolute_import


class DocLoadingError(Exception):
    """
    Exception to be raised when apidoc could not be loaded.
    """


class MissingArgumentsError(Exception):
    """
    Exception to be raised when required arguments are missing.
    """


class InvalidArgumentTypesError(Exception):
    """
    Exception to be raised when arguments are of the wrong type.
    """
