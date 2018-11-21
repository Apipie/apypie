import re

HTML_STRIP = re.compile(r'<\/?[^>]+?>')


class Param:
    """
    Apipie Param
    """

    def __init__(self, **kwargs):
        self.allow_nil = kwargs.get('allow_nil')
        self.description = HTML_STRIP.sub('', kwargs.get('description'))
        self.expected_type = kwargs.get('expected_type')
        self.full_name = kwargs.get('full_name')
        self.name = kwargs.get('name')
        self.params = [Param(**param) for param in kwargs.get('params', [])]
        self.required = bool(kwargs.get('required'))
        self.validator = kwargs.get('validator')
