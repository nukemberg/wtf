from __future__ import print_function

__author__ = 'avishai'

import json
import logging
import click
import colorama
from functools import partial
import os
import yaml
import collections
from pluginbase import PluginBase
import inspect
from wtf.plugin import Plugin
from concurrent.futures import ThreadPoolExecutor
import pkg_resources


WTF_CONF_YAML = "/etc/wtf.yaml"
WTF_CONF_JSON = "/etc/wtf.json"

default_common_conf = {
    'plugin_path': [],
    'threads': 4
}


def read_conf(conf_file):
    if conf_file is None:
        conf_files = [WTF_CONF_JSON, WTF_CONF_YAML]
    else:
        conf_files = [conf_file]

    for file in conf_files:
        if os.path.isfile(file):
            with open(file, 'r') as f:
                if file.endswith(".json"):
                    return json.load(f)
                elif file.endswith(".yaml") or file.endswith(".yml"):
                    return yaml.load(f)
                else:
                    logging.error("Can't identify file type from extension")
                    raise RuntimeError("Could not parse config file")
    return {}


@click.command()
@click.option("--all", "verbose", help="Show all output, even if no problem is detected", is_flag=True, default=False)
@click.option("-c", "--config", "config", help="Config file location", metavar="CONFIG_FILE")
def main(verbose, config):
    logging.basicConfig(level=logging.WARN, format="%(levelname)s: %(message)s")
    conf = read_conf(config)
    conf['common'] = dict(default_common_conf.items() + conf.get('common', {}).items())
    wtf_data = run_plugins(conf)
    colorama.init()

    for plugin_data in wtf_data:
        if plugin_data.get('info'):
            print(plugin_data['info'])
        if plugin_data.get('problem'):
            if plugin_data.get('extra_info'):
                print(colorama.Fore.RED + str(plugin_data['extra_info']) + colorama.Fore.RESET)
            print(colorama.Fore.RED + plugin_data['problem'] + colorama.Fore.RESET)
        elif verbose and plugin_data.get('extra_info'):
            print(plugin_data['extra_info'])


def run_plugins(conf):
    """
    Load all plugins and run them

    :param conf:
    :type conf: dict
    :return: a list of plugin outputs
    :rtype: list[dict]
    """
    plugin_path = [pkg_resources.resource_filename('wtf', 'plugins')]
    try:
        plugin_path += conf['common']['plugin_path']
    except (KeyError, TypeError):
        pass

    plugin_base = PluginBase('wtf.plugins')
    plugin_source = plugin_base.make_plugin_source(searchpath=plugin_path)

    plugins = []
    for plugin_name in plugin_source.list_plugins():
        plugin_module = plugin_source.load_plugin(plugin_name)
        _classes = inspect.getmembers(plugin_module, inspect.isclass)
        plugins += [_class for name, _class in _classes if issubclass(_class, Plugin) and not _class == Plugin]

    with ThreadPoolExecutor(max_workers=conf['common']['threads']) as executor:
        future_results = [executor.submit(run_plugin, conf, plugin) for plugin in plugins]

    return [res.result() for res in future_results if res.result()]


def run_plugin(conf, plugin):
    """
    :param conf:
    :type conf: dict
    :param plugin:
    :type plugin: wtf.plugin.Plugin
    :return:
    """
    plugin_conf = conf.get(plugin.name(), {})
    plugin_conf['common'] = conf.get('common', {})
    plugin = plugin(plugin_conf)
    try:
        if plugin.enabled():
            plugin_res = plugin.run()
            if not isinstance(plugin_res, collections.Mapping):
                raise RuntimeError("Plugin returned wrong type")
            return plugin_res
    except Exception:
        logging.warn("Plugin %s failed", plugin.name, exc_info=True)
    return None

if __name__ == '__main__':
    main()
