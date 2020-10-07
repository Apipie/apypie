"""
Apypie Example module
"""

import re


EXAMPLE_PARSER = re.compile(r'(\w+)\s+([^\n]*)\n?(.*)\n(\d+)\n(.*)', re.DOTALL)


class Example(object):  # pylint: disable=too-few-public-methods
    """
    Apipie Example
    """

    def __init__(self, http_method, path, args, status, response):  # pylint: disable=too-many-arguments
        # type: (str, str, str, str, str) -> None
        self.http_method = http_method
        self.path = path
        self.args = args
        self.status = int(status)
        self.response = response

    @classmethod
    def parse(cls, example):
        """
        Parse an example from an apidoc string

        :returns: The parsed :class:`Example`
        """
        parsed = EXAMPLE_PARSER.match(example)
        return cls(*parsed.groups())
