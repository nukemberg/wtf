from mock import Mock, create_autospec
from wtf.plugins import Plugin
import wtf

__author__ = 'avishai'

import unittest

class DummyBadPlugin(Plugin):
    def run(self):
        raise RuntimeError()

class DummyMalformedPlugin(Plugin):
    def run(self):
        return (1, 2)

class PluginRunnerTests(unittest.TestCase):
    def testPluginError(self):
        self.assertEqual(wtf.run_plugin({}, DummyBadPlugin), None)

    def testPluginMalformed(self):
        self.assertEqual(wtf.run_plugin({}, DummyMalformedPlugin), None)

    def testPluginConf(self):
        "config dict should be passed to plugin"
        p = create_autospec(Plugin)
        p.name = '**name**'
        wtf.run_plugin({'**name**': {'k': 'v'}}, p)
        p.assert_called_once_with({'k': 'v'})
