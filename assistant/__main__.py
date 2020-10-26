__package__ = 'assistant'

import glob
from os import path
from os import mkdir
import importlib
import argparse
from .plugin_manager import PluginManager
from .config_manager import ConfigManager
from .log_manager import LogManager
from .database_manager import DatabaseManager


def arg_parser_portion():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', dest='interface', help='TUI or GUI', default='TUI')
    parser.add_argument('args', help='Any other arguments', default='', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    return args


def init_user_interface(log_manager, args):
    wanted_user_interface = args.interface
    _instance = None
    if "GUI" in wanted_user_interface:
        wanted_user_interface = "GraphicalUserInterface"
    else:
        wanted_user_interface = "TextUserInterface"
    try:
        _mod = importlib.import_module('assistant.' + wanted_user_interface)
        _class = getattr(_mod, wanted_user_interface)
        _instance = _class(log_manager, args.args)
    except ImportError as err:
        print("Cannot find associated module:", err)

    if _instance:
        _instance.go()
    return _instance


def read_configs(log_manager):
    conf_manager = ConfigManager(log_manager)
    conf_manager.go()
    return conf_manager


def prep_log_manager():
    log_man = LogManager()
    return log_man


def prep_plugin_manager(log_manager, conf_manager, database, args):
    plug_manager = PluginManager(log_manager, args)
    plug_manager.handle_component_config(conf_manager.return_config_data())
    plug_manager.go()
    plug_manager.set_database_connection(database)
    plug_manager.associate_database_to_plugins()
    plug_manager.prepare_plugins()
    return plug_manager


def init_main_routine():
    for path_check in glob.glob("./assistant", recursive=True):
        if path.exists(path_check):
            if not path.exists(path_check + "/data"):
                mkdir(path_check + "/data")
    args = arg_parser_portion()
    log_manager = prep_log_manager()
    conf_manager = read_configs(log_manager)
    log_manager.handle_component_config(conf_manager.return_config_data())
    database = DatabaseManager(log_manager)
    database.go()
    interface = init_user_interface(log_manager, args)
    plug_manager = prep_plugin_manager(log_manager, conf_manager, database, args)
    plug_manager.make_plugins_go()
    plug_manager.send_command_all_loaded_plugins("CheckAlive")
    plug_manager.send_command_all_loaded_plugins(args.args)


init_main_routine()
