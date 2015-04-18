__author__ = 'avishai'

from wtf.plugins import Plugin
import subprocess
import json
from wtf.utils import which

DEFAULT_FACTS = ['operatingsystem', 'operatingsystemrelease', 'virtual', 'hostname', 'fqdn', 'architecture',
                 'memorysize', 'swapsize', 'processorcount']

class Facter(Plugin):

    def run(self):
        p = subprocess.Popen(["facter", "--json"], stdout=subprocess.PIPE)
        facts = self._conf.get('facts', DEFAULT_FACTS)
        facter_facts = dict(filter(lambda (k, v): k in facts,json.load(p.stdout).iteritems()))
        return dict(problem=False, info=facter_facts)

    def enabled(self):
        return which("facter") is not None