__author__ = 'avishai'

from mock import Mock
from wtf.plugin import Plugin
import wtf
from unittest2 import TestCase


class DummyBadPlugin(Plugin):
    def run(self):
        raise RuntimeError()


class DummyMalformedPlugin(Plugin):
    def run(self):
        return (1, 2)


class DummyGoodPlugin(Plugin):
    def run(self):
        return dict(problem="problem", info="info", extra_info="extra_info")


class PluginRunnerTests(TestCase):
    def testPluginError(self):
        self.assertEqual(wtf.run_plugin({}, DummyBadPlugin), None)

    def testPluginMalformed(self):
        self.assertEqual(wtf.run_plugin({}, DummyMalformedPlugin), None)

    def testPluginConf(self):
        "config dict should be passed to plugin"
        p = Mock(spec=Plugin)
        p.name = Mock(return_value='**name**')
        wtf.run_plugin({'**name**': {'k': 'v'}}, p)
        p.assert_called_once_with({'k': 'v', 'common': {}})

    def testPluginOK(self):
        self.assertEqual(dict(problem="problem", info="info", extra_info="extra_info"),
                         wtf.run_plugin({}, DummyGoodPlugin))
