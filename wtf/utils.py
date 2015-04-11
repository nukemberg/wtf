__author__ = 'avishai'

import os


def is_exe(fpath):
    return os.access(fpath, os.X_OK)

# from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None