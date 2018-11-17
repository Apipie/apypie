from __future__ import print_function, absolute_import

class Route:
    """
    Apipie Route
    """

    def __init__(self, path, method, description=""):
        self.path = path
        self.method = method.lower()
        self.description = description
