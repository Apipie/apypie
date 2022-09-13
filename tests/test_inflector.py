from __future__ import print_function

import apypie


def test_inflector():
    inflector = apypie.Inflector()
    assert inflector.pluralize('word') == 'words'
    assert inflector.singularize('words') == 'word'
    assert inflector.pluralize('gpg_key') == 'gpg_keys'
    assert inflector.pluralize('equipment') == 'equipment'
    assert inflector.pluralize('medium') == 'media'
    assert inflector.singularize('errata') == 'erratum'
