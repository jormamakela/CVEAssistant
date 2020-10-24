__package__ = 'assistant'

import importlib
import sys
import argparse
from .plugin_manager import PluginManager
from .config_manager import ConfigManager
from .TextUserInterface import TextUserInterface
from .GraphicalUserInterface import GraphicalUserInterface

parser = argparse.ArgumentParser()
parser.add_argument('--interface', dest='interface', help='TUI or GUI', default='GUI')
parser.add_argument('args', help='Any other arguments', default='', nargs=argparse.REMAINDER)
args = parser.parse_args()

wanted_user_interface = args.interface
_instance = None
if "GUI" in wanted_user_interface:
    wanted_user_interface = "GraphicalUserInterface"
else:
    wanted_user_interface = "TextUserInterface"
try:
    _mod = importlib.import_module('assistant.' + wanted_user_interface)
    _class = getattr(_mod, wanted_user_interface)
    _instance = _class(args.args)
except ImportError as err:
    print("Cannot find associated module:", err)

if _instance:
    _instance.go()
