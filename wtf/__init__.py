__author__ = 'avishai'

import click
import colorama
from linux import Df, LoadAvg
from facter import Facter

@click.command()
@click.option("--all", "verbose", help="Show all output, even if no problem is detected", is_flag=True, default=False)
def main(verbose):
    colorama.init()

    plugins = [Df, LoadAvg, Facter]

    info = filter(lambda x: x is not None, map(run_plugin, plugins))

    for problem, normal_info, extra_info in info:
        if normal_info:
            print normal_info
        if problem:
            print colorama.Fore.RED + extra_info + colorama.Fore.RESET
            print colorama.Fore.RED + problem + colorama.Fore.RESET
        elif verbose and extra_info:
            print extra_info


def run_plugin(plugin):
    plugin = plugin()
    if plugin.enabled:
        return plugin.run()
    return None

if __name__ == '__main__':
    main()