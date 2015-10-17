import subprocess
from wtf.plugin import Plugin
import re

__author__ = 'avishai'

"""
TX errors = CRC, checksum mismatch
Frame = Packet fails to end on a 32bit/4 byte boundary
Not sure if this includes small packets ( <64bytes )
or large packets.
Collisions = This interface is running half duplex.
It is detecting TX and RX packets at the same time.
This is bad in a HDuplex environment (Hubs)
Switched environments operate full duplex.
Collision detection is disabled in FD mode.
A mismatch in duplex is very bad for throughput.
(Switch = FD but Host = HD)
The HDuplex device will terminate transmission if collisions
are detected.
Some devices used to report late collisions which were very
bad in hub environments.
Carrier = Loss of link pulse. Sometimes recreated by removing and
installing the Ethernet cable.
If this counter is high, the link is flapping. (up/down)
Either this Ethernet chip is having issues or the device at the
other end of the cable is having issues
Overruns = The NIC has a Buffer of X bytes and this filled and was
exceeded before the buffer could be emptied.
The Excess is the overrun.

These days, Full Duplex switch links are the norm. Only TX and RX packets should be incrementing. Carrier is typically a low number less than 10. This will be higher on linux boxes that go an entire year between reboots. The important thing to look at is the rate at which the errors are incrementing.
"""


class Ifconfig(Plugin):
    def run(self):
        data = self._read_proc_net_dev()
        ignored_ifaces = self._conf.get('ignored', [])
        filtered_data = dict(filter(lambda (iface, iface_info): iface not in ignored_ifaces, data.items()))
        bad_interfaces = dict(filter(self._iface_is_bad, filtered_data.items()))
        if bad_interfaces:
            return dict(problem="The following NICs appear to have issues: %s\n"
                            "Please note that ifconfig counters need to be reset in order to avoid detecting old errors"
                            % ", ".join(bad_interfaces.keys()))
        else:
            return dict()

    def _read_proc_net_dev(self):
        with open('/proc/net/dev') as f:
            # skip header lines
            next(f)

            rx_columns, tx_columns = map(lambda l: re.split('\s+', l), next(f).strip().split('|')[1:])
            rx_columns = ['rx_' + column_name for column_name in rx_columns]
            tx_columns = ['tx_' + column_name for column_name in tx_columns]

            dev_stats = {}
            for line in f:
                dev, raw_stats = line.strip().split(':', 1)
                stats = map(int, re.split('\s+', raw_stats.strip()))
                dev_stats[dev] = dict(zip(rx_columns + tx_columns, stats))

        return dev_stats

    def _iface_is_bad(self, (iface, iface_info)):
        return any(v > 0 for (k, v) in iface_info.items()
                   if '_' in k and k.split('_')[1] in ('tx_colls', 'tx_drop', 'tx_errs', 'rx_drop', 'rx_errs'))
