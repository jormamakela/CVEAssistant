import glob
from .helpers.common_file_helper import *


class ConfigManager:

    def __init__(self, log_manager):
        self.component_name = "ConfigManager"
        self.component_version = "0.0.0"
        self.config_file_name = "settings.conf"
        self.config_data = None
        self.config_file_rel_path = None
        self.config_data_startswith = "ConfigManager"
        self.logger = log_manager

    def go(self):
        self.get_config_file_path()
        self.read_config_file_data()
        return self.return_config_data()

    def get_config_file_path(self):
        for file in glob.glob("./**/" + self.config_file_name, recursive=True):
            self.config_file_rel_path = file

    def read_config_file_data(self):
        data = read_file_as_string(self.config_file_rel_path)
        self.config_data = parse_any_dict_from_string(data)

    def return_config_data(self):
        return self.config_data
