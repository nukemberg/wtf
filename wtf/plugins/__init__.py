__author__ = 'avishai'

from abc import abstractmethod, ABCMeta

# This is the prototype of a plugin

class Plugin(object):
    __metaclass__ = ABCMeta

    def __init__(self, conf):
        self._conf = conf

    # override this property if you want to enable a plugin dynamically
    @property
    def enabled(self):
        return True

    @property
    def name(self):
        return type(self).__name__.lower()

    @abstractmethod
    def run(self):
        pass