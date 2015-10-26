__author__ = 'avishai'

import pkg_resources
from pluginbase import PluginBase

plugins_path = pkg_resources.resource_filename('wtf', 'plugins')
plugin_base = PluginBase('wtf.plugins')
plugin_source = plugin_base.make_plugin_source(searchpath=[plugins_path])


def load_plugin(name):
    return plugin_source.load_plugin(name)
