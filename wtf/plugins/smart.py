from wtf.plugin import Plugin
from wtf.utils import which
import subprocess
import os

# TODO: report specific failures


class SmartMon(Plugin):
    def run(self):
        failed_devices = []
        for dev in self._devices():
            p = subprocess.Popen('smartctl')
            exit_status = p.wait()
            smart_failed_bit = (exit_status >> 2) & 1
            disk_failing_bit = (exit_status >> 3) & 1
            prefail_bit = (exit_status >> 4) & 1
            if smart_failed_bit or disk_failing_bit or prefail_bit:
                failed_devices.append(dev)

        if failed_devices:
            return dict(problem=', '.join(failed_devices) + ' have SMART failures')

    def enabled(self):
        return which('smartctl')

    def _devices(self):
        return os.listdir('/sys/block')