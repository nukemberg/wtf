__author__ = 'avishai'

# This is the prototype of a plugin

class Plugin(object):
    def __init__(self, conf):
        self._conf = conf

    # override this property if you want to enable a plugin dynamically
    # alternatively, you can provide _is_enabled private method in your class
    @property
    def enabled(self):
        if hasattr(self, '_is_enabled'):
            return self._is_enabled()
        return True

    @property
    def name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return type(self).__name__.lower()

    def run(self):
        raise NotImplemented()