__author__ = 'avishai'

from abc import abstractmethod, ABCMeta


# This is the prototype of a plugin
class Plugin(object):
    __metaclass__ = ABCMeta

    def __init__(self, conf):
        self._conf = conf
        """:type: dict"""

    # override this property if you want to enable a plugin dynamically
    def enabled(self):
        return True

    @classmethod
    def name(cls):
        return cls.__name__.split('.')[-1].lower()

    @abstractmethod
    def run(self):
        """Run a plugin and return relevant data. Plugins should return a dict"""
        pass