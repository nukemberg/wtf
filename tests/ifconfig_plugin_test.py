from unittest import TestCase
from wtf.plugins.ifconfig import Ifconfig

__author__ = 'avishai'

ifconfig_output = """lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 0  (Local Loopback)
        RX packets 248246  bytes 3712662182 (3.4 GiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 248246  bytes 3712662182 (3.4 GiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

an1: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 192.168.122.1  netmask 255.255.255.0  broadcast 192.168.122.255
        ether 0e:a7:0a:1b:24:f4  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2  bytes 96 (96.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.0.0.2  netmask 255.255.255.0  broadcast 10.0.0.255
        inet6 fe80::7e7a:91ff:fe3f:de78  prefixlen 64  scopeid 0x20<link>
        ether 7c:7a:91:3f:de:78  txqueuelen 1000  (Ethernet)
        RX packets 1649420  bytes 1018692405 (971.5 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 512553  bytes 81943077 (78.1 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

"""

class IfconfigPluginTest(TestCase):
    def testCmdParser(self):
        self.maxDiff = None
        p = Ifconfig({})
        p_output = p._parse_ifconfig_output(ifconfig_output)
        expected = {'lo': {'mtu': '65536', 'type': 'loop', 'rx_errors': 0, 'rx_dropped': 0, 'rx_overruns': 0,
                           'tx_errors': 0, 'tx_dropped': 0, 'tx_overruns': 0, 'tx_carrier': 0, 'tx_collisions': 0},
                    'eth0': {'type': 'ether', 'mtu': '1500', 'rx_errors': 0, 'rx_dropped': 0, 'rx_overruns': 0,
                             'tx_errors': 0, 'tx_dropped': 0, 'tx_overruns': 0, 'tx_carrier': 0, 'tx_collisions': 0},
                    'an1': {'type': 'ether', 'mtu': '1500', 'rx_errors': 0, 'rx_dropped': 0, 'rx_overruns': 0,
                            'tx_errors': 0, 'tx_dropped': 0, 'tx_overruns': 0, 'tx_carrier': 0, 'tx_collisions': 0}}
        self.assertDictEqual(p_output, expected)