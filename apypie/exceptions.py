from __future__ import print_function, absolute_import

from sys import version_info


class Printable(object):
    message = ''

    def print(self):
        print(self.message.encode("utf-8") if version_info.major == 2 else self.message)


class DocLoadingError(Exception, Printable):
    pass
