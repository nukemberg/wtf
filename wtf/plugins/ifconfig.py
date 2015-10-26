import subprocess
from wtf.plugin import Plugin
import re
import psutil

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
        ignored_ifaces = self._conf.get('ignored', ['lo'])
        data = dict((k, dict(v.__dict__)) for k, v in psutil.net_io_counters(True).items() if k not in ignored_ifaces)
        ifaces_stats = dict((k, dict(v.__dict__)) for k, v in psutil.net_if_stats().items() if k not in ignored_ifaces)
        ifaces_down = [k for k, v in ifaces_stats.items() if not v['isup']]

        bad_interfaces = dict(filter(self._iface_is_bad, data.items()))

        problems = []
        if ifaces_down:
            problems.append("The following interfaces are down: %s" % ",".join(ifaces_down))

        if bad_interfaces:
            problems.append("The following NICs appear to have issues: %s\n"
                            "Please note that ifconfig counters need to be reset in order to avoid detecting old errors"
                            % ", ".join(bad_interfaces.keys()))

        return dict(problem="\n".join(problems), extra_info=data)

    def _iface_is_bad(self, (iface, iface_info)):
        return any(iface_info[k] > 0 for k in ('dropout', 'dropin', 'errout', 'errin'))
