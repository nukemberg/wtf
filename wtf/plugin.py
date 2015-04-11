__author__ = 'avishai'

# This is the prototype of a plugin

class Plugin(object):
    def __init__(self):
        pass

    # override this property if you want to enable a plugin dynamically
    # alternatively, you can provide _is_enabled private method in your class
    @property
    def enabled(self):
        if hasattr(self, '_is_enabled'):
            return self._is_enabled()
        return True

    def run(self):
        raise NotImplemented()