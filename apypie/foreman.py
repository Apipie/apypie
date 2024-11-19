"""
Apypie Foreman module

opinionated helpers to use Apypie with Foreman
"""
import time

from typing import cast, Optional, Set, Tuple

from apypie.api import Api

from apypie.resource import Resource  # pylint: disable=unused-import  # noqa: F401

# Foreman supports "per_page=all" since 2.2 (https://projects.theforeman.org/issues/29909)
# But plugins, especially Katello, do not: https://github.com/Katello/katello/pull/11126
# To still be able to fetch all results without pagination, we have this constant for now
PER_PAGE = 2 << 31


class ForemanApiException(Exception):
    """
    General Exception, raised by any issue in ForemanApi
    """

    def __init__(self, msg, error=None):
        if error:
            super().__init__(f'{msg} - {error}')
        else:
            super().__init__(msg)

    @classmethod
    def from_exception(cls, exc, msg):
        """
        Create a ForemanException from any other Exception

        Especially useful to gather the error message from HTTP responses.
        """
        error = None
        if hasattr(exc, 'response') and exc.response is not None:
            try:
                response = exc.response.json()
                if 'error' in response:
                    error = response['error']
                else:
                    error = response
            except Exception:  # pylint: disable=broad-except
                error = exc.response.text
        return cls(msg=msg, error=error)


class ForemanApi(Api):
    """
    `apypie.Api` with default settings and helper functions for Foreman

    Usage::

      >>> import apypie
      >>> api = apypie.ForemanApi(uri='https://foreman.example.com', username='admin', password='changeme')
    """

    def __init__(self, **kwargs):
        self.task_timeout = kwargs.pop('task_timeout', 60)
        self.task_poll = 4
        kwargs['api_version'] = 2
        super().__init__(**kwargs)

    def _resource(self, resource: str) -> 'Resource':
        if resource not in self.resources:
            raise ForemanApiException(msg=f"The server doesn't know about {resource}, is the right plugin installed?")
        return self.resource(resource)

    def _resource_call(self, resource: str, *args, **kwargs) -> Optional[dict]:
        return self._resource(resource).call(*args, **kwargs)

    def _resource_prepare_params(self, resource: str, action: str, params: dict) -> dict:
        api_action = self._resource(resource).action(action)
        return api_action.prepare_params(params)

    def resource_action(self, resource: str, action: str, params: dict, options=None, data=None, files=None,  # pylint: disable=too-many-arguments
                        ignore_task_errors: bool = False) -> Optional[dict]:
        """
        Perform a generic action on a resource

        Will wait for tasks if the action returns one
        """
        resource_payload = self._resource_prepare_params(resource, action, params)
        if options is None:
            options = {}
        try:
            result = self._resource_call(resource, action, resource_payload, options=options, data=data, files=files)
            is_foreman_task = isinstance(result, dict) and 'action' in result and 'state' in result and 'started_at' in result
            if result and is_foreman_task:
                result = self.wait_for_task(result, ignore_errors=ignore_task_errors)
        except Exception as exc:
            msg = f'Error while performing {action} on {resource}: {exc}'
            raise ForemanApiException.from_exception(exc, msg) from exc
        return result

    def wait_for_task(self, task: dict, ignore_errors: bool = False) -> dict:
        """
        Wait for a foreman-tasks task, polling it every ``self.task_poll`` seconds.

        Will raise a ForemanApiException when task has not finished in ``self.task_timeout`` seconds.
        """
        duration = self.task_timeout
        while task['state'] not in ['paused', 'stopped']:
            duration -= self.task_poll
            if duration <= 0:
                raise ForemanApiException(msg=f"Timeout waiting for Task {task['id']}")
            time.sleep(self.task_poll)

            resource_payload = self._resource_prepare_params('foreman_tasks', 'show', {'id': task['id']})
            task = cast(dict, self._resource_call('foreman_tasks', 'show', resource_payload))
        if not ignore_errors and task['result'] != 'success':
            msg = f"Task {task['action']}({task['id']}) did not succeed. Task information: {task['humanized']['errors']}"
            raise ForemanApiException(msg=msg)
        return task

    def show(self, resource: str, resource_id: int, params: Optional[dict] = None) -> Optional[dict]:
        """
        Execute the ``show`` action on an entity.

        :param resource: Plural name of the api resource to show
        :param resource_id: The ID of the entity to show
        :param params: Lookup parameters (i.e. parent_id for nested entities)

        :return: The entity
        """
        payload = {'id': resource_id}
        if params:
            payload.update(params)
        return self.resource_action(resource, 'show', payload)

    def list(self, resource: str, search: Optional[str] = None, params: Optional[dict] = None) -> list:
        """
        Execute the ``index`` action on an resource.

        :param resource: Plural name of the api resource to show
        :param search: Search string as accepted by the API to limit the results
        :param params: Lookup parameters (i.e. parent_id for nested entities)

        :return: List of results
        """
        payload: dict = {'per_page': PER_PAGE}
        if search is not None:
            payload['search'] = search
        if params:
            payload.update(params)

        result = self.resource_action(resource, 'index', payload)
        if result:
            return result['results']
        return []

    def create(self, resource: str, desired_entity: dict, params: Optional[dict] = None) -> Optional[dict]:
        """
        Create entity with given properties

        :param resource: Plural name of the api resource to manipulate
        :param desired_entity: Desired properties of the entity
        :param params: Lookup parameters (i.e. parent_id for nested entities)

        :return: The new current state of the entity
        """
        payload = desired_entity.copy()
        if params:
            payload.update(params)
        return self.resource_action(resource, 'create', payload)

    def update(self, resource: str, desired_entity: dict, params: Optional[dict] = None) -> Optional[dict]:
        """
        Update entity with given properties

        :param resource: Plural name of the api resource to manipulate
        :param desired_entity: Desired properties of the entity
        :param params: Lookup parameters (i.e. parent_id for nested entities)

        :return: The new current state of the entity
        """
        payload = desired_entity.copy()
        if params:
            payload.update(params)
        return self.resource_action(resource, 'update', payload)

    def delete(self, resource: str, current_entity: dict, params: Optional[dict] = None) -> None:
        """
        Delete a given entity

        :param resource: Plural name of the api resource to manipulate
        :param current_entity: Current properties of the entity
        :param params: Lookup parameters (i.e. parent_id for nested entities)

        :return: The new current state of the entity
        """
        payload = {'id': current_entity['id']}
        if params:
            payload.update(params)
        entity = self.resource_action(resource, 'destroy', payload)

        # this is a workaround for https://projects.theforeman.org/issues/26937
        if entity and isinstance(entity, dict) and 'error' in entity and 'message' in entity['error']:
            raise ForemanApiException(msg=entity['error']['message'])

    def validate_payload(self, resource: str, action: str, payload: dict) -> Tuple[dict, Set[str]]:
        """
        Check whether the payload only contains supported keys.

        :param resource: Plural name of the api resource to check
        :param action: Name of the action to check payload against
        :param payload: API paylod to be checked

        :return: The payload as it can be submitted to the API and set of unssuported parameters
        """
        filtered_payload = self._resource_prepare_params(resource, action, payload)
        unsupported_parameters = set(payload.keys()) - _recursive_dict_keys(filtered_payload)
        return (filtered_payload, unsupported_parameters)


def _recursive_dict_keys(a_dict: dict) -> set:
    """Find all keys of a nested dictionary"""
    keys = set(a_dict.keys())
    for value in a_dict.values():
        if isinstance(value, dict):
            keys.update(_recursive_dict_keys(value))
    return keys
