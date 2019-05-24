from __future__ import print_function, absolute_import


class Route:
    """
    Apipie Route
    """

    def __init__(self, path, method, description=""):
        self.path = path
        self.method = method.lower()
        self.description = description

    @property
    def params_in_path(self):
        return [part[1:] for part in self.path.split('/') if part.startswith(':')]

    def path_with_params(self, params=None):
        if params is None:
            return self.path
        else:
            result = self.path
            for param in self.params_in_path:
                if param in params:
                    result = result.replace(':{}'.format(param), str(params[param]))
                else:
                    raise KeyError("missing param '{}' in parameters".format(param))
            return result
