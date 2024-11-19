"""
Apypie Inflector module

Based on ActiveSupport Inflector (https://github.com/rails/rails.git)
Inflection rules taken from davidcelis's Inflections (https://github.com/davidcelis/inflections.git)
"""

import re

from typing import Iterable, Tuple  # pylint: disable=unused-import  # noqa: F401


class Inflections(object):
    """
    Inflections - rules how to convert words from singular to plural and vice versa.
    """

    def __init__(self):
        self.plurals = []
        self.singulars = []
        self.uncountables = []
        self.humans = []
        self.acronyms = {}
        self.acronym_regex = r'/(?=a)b/'

    def acronym(self, word):
        # type: (str) -> None
        """
        Add a new acronym.
        """

        self.acronyms[word.lower()] = word
        self.acronym_regex = '|'.join(self.acronyms.values())

    def plural(self, rule, replacement):
        # type: (str, str) -> None
        """
        Add a new plural rule.
        """

        if rule in self.uncountables:
            self.uncountables.remove(rule)
        if replacement in self.uncountables:
            self.uncountables.remove(replacement)

        self.plurals.insert(0, (rule, replacement))

    def singular(self, rule, replacement):
        # type: (str, str) -> None
        """
        Add a new singular rule.
        """

        if rule in self.uncountables:
            self.uncountables.remove(rule)
        if replacement in self.uncountables:
            self.uncountables.remove(replacement)

        self.singulars.insert(0, (rule, replacement))

    def irregular(self, singular, plural):
        # type: (str, str) -> None
        """
        Add a new irregular rule
        """

        if singular in self.uncountables:
            self.uncountables.remove(singular)
        if plural in self.uncountables:
            self.uncountables.remove(plural)

        sfirst = singular[0]
        srest = singular[1:]

        pfirst = plural[0]
        prest = plural[1:]

        if sfirst.upper() == pfirst.upper():
            self.plural(r'(?i)({}){}$'.format(sfirst, srest), r'\1' + prest)
            self.plural(r'(?i)({}){}$'.format(pfirst, prest), r'\1' + prest)

            self.singular(r'(?i)({}){}$'.format(sfirst, srest), r'\1' + srest)
            self.singular(r'(?i)({}){}$'.format(pfirst, prest), r'\1' + srest)
        else:
            self.plural(r'{}(?i){}$'.format(sfirst.upper(), srest), pfirst.upper() + prest)
            self.plural(r'{}(?i){}$'.format(sfirst.lower(), srest), pfirst.lower() + prest)
            self.plural(r'{}(?i){}$'.format(pfirst.upper(), prest), pfirst.upper() + prest)
            self.plural(r'{}(?i){}$'.format(pfirst.lower(), prest), pfirst.lower() + prest)

            self.singular(r'{}(?i){}$'.format(sfirst.upper(), srest), sfirst.upper() + srest)
            self.singular(r'{}(?i){}$'.format(sfirst.lower(), srest), sfirst.lower() + srest)
            self.singular(r'{}(?i){}$'.format(pfirst.upper(), prest), sfirst.upper() + srest)
            self.singular(r'{}(?i){}$'.format(pfirst.lower(), prest), sfirst.lower() + srest)

    def uncountable(self, *words):
        """
        Add new uncountables.
        """

        self.uncountables.extend(words)

    def human(self, rule, replacement):
        # type: (str, str) -> None
        """
        Add a new humanize rule.
        """

        self.humans.insert(0, (rule, replacement))


class Inflector(object):
    """
    Inflector - perform inflections
    """

    def __init__(self):
        # type: () -> None
        self.inflections = Inflections()
        self.inflections.plural(r'$', 's')
        self.inflections.plural(r'(?i)([sxz]|[cs]h)$', r'\1es')
        self.inflections.plural(r'(?i)([^aeiouy]o)$', r'\1es')
        self.inflections.plural(r'(?i)([^aeiouy])y$', r'\1ies')

        self.inflections.singular(r'(?i)s$', r'')
        self.inflections.singular(r'(?i)(ss)$', r'\1')
        self.inflections.singular(r'([sxz]|[cs]h)es$', r'\1')
        self.inflections.singular(r'([^aeiouy]o)es$', r'\1')
        self.inflections.singular(r'(?i)([^aeiouy])ies$', r'\1y')

        self.inflections.irregular('child', 'children')
        self.inflections.irregular('man', 'men')
        self.inflections.irregular('medium', 'media')
        self.inflections.irregular('move', 'moves')
        self.inflections.irregular('person', 'people')
        self.inflections.irregular('self', 'selves')
        self.inflections.irregular('sex', 'sexes')
        self.inflections.irregular('erratum', 'errata')

        self.inflections.uncountable('equipment', 'information', 'money', 'species', 'series', 'fish', 'sheep', 'police')

    def pluralize(self, word):
        # type: (str) -> str
        """
        Pluralize a word.
        """

        return self._apply_inflections(word, self.inflections.plurals)

    def singularize(self, word):
        # type: (str) -> str
        """
        Singularize a word.
        """

        return self._apply_inflections(word, self.inflections.singulars)

    def _apply_inflections(self, word, rules):
        # type: (str, Iterable[Tuple[str, str]]) -> str
        result = word

        if word != '' and result.lower() not in self.inflections.uncountables:
            for (rule, replacement) in rules:
                result = re.sub(rule, replacement, result)
                if result != word:
                    break

        return result
