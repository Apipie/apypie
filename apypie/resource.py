from __future__ import print_function, absolute_import

from apypie.action import Action

try:
    from typing import Optional, Any, List, TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from apypie.api import Api


class Resource:
    """
    Apipie Resource
    """

    def __init__(self, api, name):
        # type: (Api, str) -> None
        self.api = api
        self.name = name

    @property
    def actions(self):
        # type: () -> List
        return sorted([method['name'] for method in self.api.apidoc['docs']['resources'][self.name]['methods']])

    def action(self, name):
        # type: (str) -> Action
        if self.has_action(name):
            return Action(name, self.name, self.api)
        else:
            message = "Unknown action '{}'. Supported actions: {}".format(name, ', '.join(sorted(self.actions)))
            raise KeyError(message)

    def has_action(self, name):
        # type: (str) -> bool
        return name in self.actions

    def call(self, action, params={}, headers={}, options={}, data=None, files=None):
        # type: (str, dict, dict, dict, Optional[Any], Optional[dict]) -> dict
        return self.api.call(self.name, action, params, headers, options, data, files)
