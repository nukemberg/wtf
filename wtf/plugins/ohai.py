import json
import subprocess
from wtf.plugins import Plugin
from wtf.utils import which, get_in, flatten_key_name

__author__ = 'avishai'

DEFAULT_ATTRIBUTES = ["platform", "platform_version", "hostname", "fqdn", ('kernel', 'machine'),
                      ('virtualization', 'system'), ('cpu', 'total'), ('memory', 'total'), ('memory', 'swap', 'total')]

class Ohai(Plugin):
    def run(self):
        attributes = self._conf.get('attributes', DEFAULT_ATTRIBUTES)
        p = subprocess.Popen("ohai", stdout=subprocess.PIPE)
        data = json.load(p.stdout)
        ohai_attributes = dict((flatten_key_name(attr), get_in(data, attr)) for attr in attributes)
        return dict(problem=False, info=ohai_attributes)

    def enabled(self):
        return bool(which("ohai"))