import unittest
from mock import patch
import psutil
from psutil._common import snicstats, snetio
from wtf.plugins.ifconfig import Ifconfig
import contextlib


class IfconfigPluginTest(unittest.TestCase):

    def setUp(self):
        self._plugin = Ifconfig({})

    def testDownIfaces(self):
        with contextlib.nested( 
            patch.object(psutil, 'net_io_counters', return_value={'lo': {}}),
            patch.object(psutil, 'net_if_stats', return_value={'eth0': snicstats(False, 0, 0, 1500)})):
            output = self._plugin.run()
            self.assertEqual(output['problem'], 'The following interfaces are down: eth0')

    def testBadIfaces(self):
        for test_snetio in [
            snetio(122312, 2312312, 3432, 34324, 11, 0, 0, 0),
            snetio(122312, 2312312, 3432, 34324, 0, 1, 0, 0),
            snetio(122312, 2312312, 3432, 34324, 0, 0, 1, 0),
            snetio(122312, 2312312, 3432, 34324, 0, 0, 0, 1)
        ]:

            with contextlib.nested(
                patch.object(psutil, 'net_io_counters', return_value={'eth0': test_snetio}),
                patch.object(psutil, 'net_if_stats', return_value={'eth0': snicstats(True, 0, 0, 1500)})):
                output = self._plugin.run()
                self.assertRegexpMatches(output['problem'], 'issues.*eth0')

    def testIfaceIgnored(self):
        plugin = Ifconfig({'ignored': ['eth0']})
        with contextlib.nested(
            patch.object(psutil, 'net_io_counters', return_value={'eth0': snetio(1122, 233, 333, 333, 1, 1, 1, 1)}),
            patch.object(psutil, 'net_if_stats', return_value={'eth0': snicstats(False, 0, 0, 1500)})):
            output = plugin.run()
            self.assertFalse(output['problem'])
