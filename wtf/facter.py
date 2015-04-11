from plugin import Plugin

__author__ = 'avishai'

import subprocess
import json
from utils import which


class Facter(Plugin):
    def run(self):
        p = subprocess.Popen(["facter", "--json"], stdout=subprocess.PIPE)
        facter_facts = json.load(p.stdout)
        return False, facter_facts, None

    def _is_enabled(self):
        return which("facter") is not None