"""
Apypie Route module
"""

from __future__ import print_function, absolute_import

from urllib.parse import quote  # type: ignore

from typing import List, Optional  # pylint: disable=unused-import  # noqa: F401


class Route(object):
    """
    Apipie Route
    """

    def __init__(self, path, method, description=""):
        # type: (str, str, str) -> None
        self.path = path
        self.method = method.lower()
        self.description = description

    @property
    def params_in_path(self):
        # type: () -> List
        """
        Params that can be passed in the path (URL) of the route.

        :returns: The params.
        """
        return [part[1:] for part in self.path.split('/') if part.startswith(':')]

    def path_with_params(self, params=None):
        # type: (Optional[dict]) -> str
        """
        Fill in the params into the path.

        :returns: The path with params.
        """
        result = self.path
        if params is not None:
            for param in self.params_in_path:
                if param in params:
                    result = result.replace(':{}'.format(param), quote(str(params[param]), safe=''))
                else:
                    raise KeyError("missing param '{}' in parameters".format(param))
        return result
