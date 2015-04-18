__author__ = 'avishai'

import procfs
import os
import multiprocessing
from wtf.plugins import Plugin

class LoadAvg(Plugin):
    def run(self):
        p = procfs.Proc()
        n_cpu = multiprocessing.cpu_count()
        loadavg = p.loadavg()

        if any(avg > n_cpu for avg in loadavg['average'].values()):
            problem = "High load average (you have %d cores)" % n_cpu
        else:
            problem = False
        loadavg_avg = dict((str(k), v) for k, v in loadavg['average'].items())
        return dict(problem=problem, info="Load avg: %(1).2f (1m), %(5).2f (5m), %(15).2f (15m)" % loadavg_avg)


class Df(Plugin):
    def _statfs(self, dev):
        try:
            return os.statvfs(dev)
        except OSError:
            pass

    def _df(self):
        def _remove_nodev_and_empty(entry):
            if len(entry) < 2: return False
            if entry[0] == 'nodev': return False
            return True

        p = procfs.Proc()
        physfs = map(lambda entry: entry[1],
                     filter(_remove_nodev_and_empty,
                            map(lambda entry: entry.split('\t'), p.filesystems.split('\n'))))
        mounts = [mountpoint for mountpoint, mountinfo in p.mounts.items() if mountinfo['type'] in physfs]

        mount_df = filter(lambda (_, y): y,
                          [(mountpoint, self._statfs(mountpoint)) for mountpoint in mounts])
        return mount_df

    def _pct(self, a, b):
        return int(float(a) / b * 100)

    def _inodes_full(self, (_, statvfs)):
        return statvfs.f_ffree == 0

    def _diskspace_full(self, (_, statvfs)):
        # TODO: don't use a fixed threshold
        return (float(statvfs.f_bfree) / statvfs.f_blocks) < 0.1

    def _statvfs_result_to_dict(self, (mountpoint, statvfs)):
        return (mountpoint, {'used_inodes_pct': self._pct(statvfs.f_favail, statvfs.f_files),
                             'used_diskspace_pct': self._pct(statvfs.f_bavail, statvfs.f_blocks)})

    def run(self):
        df_data = self._df()
        disks_with_inodes_full = filter(self._inodes_full, df_data)
        disks_full = filter(self._diskspace_full, df_data)
        problems = []
        if len(disks_full) > 0:
            problems.append("mountpoints %r are full" % [[mntpnt for mntpnt, info in disks_full]])
        if len(disks_with_inodes_full) > 0:
            problems.append("mountpoints %r are out of inodes" % [[mntpnt for mntpnt, info in disks_with_inodes_full]])

        problem = "\n".join(problems) if len(problems) > 0 else False
        return dict(problem=problem, info=None, extra_info=dict(map(self._statvfs_result_to_dict, df_data)))
