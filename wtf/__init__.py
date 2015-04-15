from __future__ import print_function

__author__ = 'avishai'

import json
import logging
import click
import colorama
from plugins.linux import Df, LoadAvg
from plugins.facter import Facter
from functools import partial
import os
import yaml

WTF_CONF_YAML = "/etc/wtf.yaml"
WTF_CONF_JSON = "/etc/wtf.json"

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
    logging.basicConfig(level=logging.WARN, format="%(level)s: %(message)s")
    colorama.init()

    plugins = [Df, LoadAvg, Facter]
    conf = read_conf(config)

    info = filter(None, map(partial(run_plugin, conf), plugins))

    for problem, normal_info, extra_info in info:
        if normal_info:
            print(normal_info)
        if problem:
            print(colorama.Fore.RED + extra_info + colorama.Fore.RESET)
            print(colorama.Fore.RED + problem + colorama.Fore.RESET)
        elif verbose and extra_info:
            print(extra_info)


def run_plugin(conf, plugin):
    """
    :param conf:
    :type conf: dict
    :param plugin:
    :type plugin: wtf.plugin.Plugin
    :return:
    """
    plugin = plugin(conf.get(plugin.name, {}))
    try:
        if plugin.enabled:
            plugin_res = plugin.run()
            if type(plugin_res) not in [tuple, list]:
                raise RuntimeError("Plugin returned wrong type")
            if len(plugin_res) != 3:
                raise RuntimeError("Plugin returned wrong number of elements")
            return plugin_res
    except Exception:
        logging.warn("Plugin %s failed", plugin.name, exc_info=True)
    return None

if __name__ == '__main__':
    main()