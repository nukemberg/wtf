from plugin import Plugin

__author__ = 'avishai'

import subprocess
import json
from utils import which

DEFAULT_FACTS = ['operatingsystem', 'operatingsystemrelease', 'virtual', 'hostname', 'fqdn', 'architecture']

class Facter(Plugin):

    def run(self):
        p = subprocess.Popen(["facter", "--json"], stdout=subprocess.PIPE)
        facts = self._conf.get('facts', DEFAULT_FACTS)
        facter_facts = dict(filter(lambda (k, v): k in facts,json.load(p.stdout).iteritems()))
        return False, facter_facts, None

    def _is_enabled(self):
        return which("facter") is not None