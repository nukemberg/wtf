import subprocess
from wtf.plugins import Plugin
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
        ifconfig_command = self._conf.get("command", "ifconfig")
        p = subprocess.Popen(ifconfig_command, stdout=subprocess.PIPE)
        data = self._parse_ifconfig_output(p.stdout.read())
        ignored_ifaces = self._conf.get('ignored_interfaces', [])
        filetered_data = dict(filter(lambda (iface, iface_info): iface not in ignored_ifaces, data.items()))

        bad_interfaces = dict(filter(self._iface_is_bad, filetered_data.items()))

        return dict(
            problem="The following NICs appear to have issues: %s\nPlease note that ifconfig counters need to be reset in order to avoid detecting old errors" % ", ".join(
                bad_interfaces.keys())) if bad_interfaces else {}

    def _parse_ifconfig_output(self, ifconfig_output):
        chunks = filter(lambda c: c, ifconfig_output.split('\n\n'))
        return dict(map(self._parse_ifconfig_chunk, chunks))

    def _parse_ifconfig_chunk(self, chunk):
        # device name
        lines = chunk.split('\n')
        info = {}

        m = re.match('^(?P<name>[0-9a-zA-Z@\.\:\-_]+):\s+.*mtu (?P<mtu>\d+)', lines[0])
        if m:
            iface_name = m.groupdict()['name']
            if 'mtu' in m.groupdict():
                info['mtu'] = m.groupdict()['mtu']
        else:
            return None, None

        for line in lines:
            if re.match('\s+inet\s', line):  # ipv4
                pass
            elif re.match('\s+inet6\s', line):  # ipv6
                pass
            else:
                m = re.match('\s+(?P<type>ether|loop).*', line)
                if m:
                    info['type'] = m.groupdict()["type"]
                    continue
                m = re.match(
                    '\s+RX errors (?P<rx_errors>\d+)\s+dropped (?P<rx_dropped>\d+)\s+overruns (?P<rx_overruns>\d+)',
                    line)
                if m:
                    info.update(dict((k, int(v)) for (k, v) in m.groupdict().items()))
                    continue
                m = re.match(
                    '\s+TX errors (?P<tx_errors>\d+)\s+dropped (?P<tx_dropped>\d+)\s+overruns (?P<tx_overruns>\d+)\s+carrier (?P<tx_carrier>\d+)\s+collisions (?P<tx_collisions>\d+)',
                    line)
                if m:
                    info.update(dict((k, int(v)) for (k, v) in m.groupdict().items()))
                    continue

        return iface_name, info

    def _iface_is_bad(self, (iface, iface_info)):
        if iface_info:
            return any(v > 0 for (k, v) in iface_info.items()
                       if '_' in k and k.split('_')[1] in ('collisions', 'dropped', 'errors', 'overruns', 'carrier'))
        return {}
