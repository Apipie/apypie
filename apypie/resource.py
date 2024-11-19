"""
Apypie Resource module
"""

from __future__ import print_function, absolute_import

from typing import Optional, Any, List, TYPE_CHECKING  # pylint: disable=unused-import  # noqa: F401

from apypie.action import Action

if TYPE_CHECKING:
    from apypie.api import Api  # pylint: disable=cyclic-import,unused-import  # noqa: F401


class Resource(object):
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
        """
        Actions available for this resource.

        :returns: The actions.
        """
        return sorted([method['name'] for method in self.api.apidoc['docs']['resources'][self.name]['methods']])

    def action(self, name):
        # type: (str) -> Action
        """
        Get an :class:`Action` for this resource.

        :param name: The name of the action.
        """
        if self.has_action(name):
            return Action(name, self.name, self.api)
        message = "Unknown action '{}'. Supported actions: {}".format(name, ', '.join(sorted(self.actions)))
        raise KeyError(message)

    def has_action(self, name):
        # type: (str) -> bool
        """
        Check whether the resource has a given action.

        :param name: The name of the action.
        """
        return name in self.actions

    def call(self, action, params=None, headers=None, options=None, data=None, files=None):  # pylint: disable=too-many-arguments
        # type: (str, Optional[dict], Optional[dict], Optional[dict], Optional[Any], Optional[dict]) -> Optional[dict]
        """
        Call the API to execute an action for this resource.

        :param action: The action to call.
        :param params: The params that should be passed to the API.
        :param headers: Additional headers to be passed to the API.
        :param options: Options
        :param data: Binary data to be submitted to the API.
        :param files: Files to be submitted to the API.

        :returns: The API response.
        """

        return self.api.call(self.name, action, params, headers, options, data, files)
