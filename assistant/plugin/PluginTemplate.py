class PluginTemplate:

    def __init__(self, log_manager, args):
        self.ui_root = None
        self.passed_args = args
        self.component_name = "PluginTemplate"
        self.component_version = "0.0.0"
        self.logger = log_manager
        self.config_data_startswith = self.component_name
        self.config_data = dict()

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)

    def handle_component_config(self, data):
        for lines in data:
            if lines.startswith(self.config_data_startswith):
                val = data[lines]
                self.config_data[lines] = val

    def prepare(self):
        self.logger.log("Prepare called at " + self.component_name + " ver " + self.component_version)

    def handle_command(self, command):
        self.logger.log("Command received at " + self.component_name + " :: " + command)
