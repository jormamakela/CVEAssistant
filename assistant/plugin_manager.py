import glob
import importlib


class PluginManager:

    def __init__(self, log_manager, args):
        self.ui_root = None
        self.passed_args = args
        self.component_name = "PluginManager"
        self.component_version = "0.0.0"
        self.logger = log_manager
        self.config_data_startswith = "Plugin"
        self.config_data = dict()
        self.plugins = dict()
        self.database = None

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)
        for plug in self.config_data:
            if "Enabled" in plug:
                plug_name = plug.split("Enabled")[0]
                plug_status = self.config_data[plug]
                if "True" in plug_status:
                    try:
                        _mod = importlib.import_module('.plugin.' + plug_name, __package__)
                        _class = getattr(_mod, plug_name)
                        _instance = _class(self.logger, self.passed_args)
                        self.plugins[plug_name] = _instance
                    except ImportError as err:
                        out = "Cannot find or initialize plugin module: " + plug_name + "-" + str(err)
                        self.logger.log(out)

    def handle_component_config(self, data):
        for lines in data:
            if lines.startswith(self.config_data_startswith):
                val = data[lines]
                self.config_data[lines] = val

    def prepare_plugins(self):
        for plugin in self.plugins:
            self.plugins[plugin].handle_component_config(self.config_data)
            self.plugins[plugin].prepare()

    def make_plugins_go(self):
        for plugin in self.plugins:
            self.plugins[plugin].go()

    def send_command_all_loaded_plugins(self, command):
        for plugin in self.plugins:
            if isinstance(command, list):
                c = command[0]
                if hasattr(self.plugins[plugin], c):
                    _method = getattr(self.plugins[plugin], c)
                    _method(command)

    def send_command_to_plugin(self, plugin, command):
        if plugin in self.plugins:
            self.plugins[plugin].handle_command(command)

    def set_database_connection(self, database_manager):
        self.database = database_manager

    def associate_database_to_plugins(self):
        for plugin in self.plugins:
            try:
                self.plugins[plugin].set_database_connection(self.database)
            except AttributeError as err:
                out = "No database receiver set for module " + plugin + " --- " + str(err)
                self.logger.log(out)
