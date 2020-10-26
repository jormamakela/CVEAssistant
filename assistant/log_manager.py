from datetime import date
from .helpers.common_file_helper import *


class LogManager:

    def __init__(self):
        self.component_name = "LogManager"
        self.component_version = "0.0.0"
        self.log_location = "/tmp/cveassistantlog_" + date.today().strftime("%Y%m%d%s")
        self.log_file_wanted = False
        self.log_to_console = True
        self.config_data_startswith = "LogManager"

    def set_write_log(self, value):
        self.log_file_wanted = value

    def set_write_console(self, value):
        self.log_to_console = value

    def set_log_path(self, path):
        self.log_location = path

    def log(self, entry):
        e = str(entry)
        if self.log_to_console:
            print(e)
        if self.log_file_wanted:
            write_append_strings_to_file(self.log_location, e + "\n")

    def handle_component_config(self, data):
        for lines in data:
            if lines.startswith(self.config_data_startswith):
                val = data[lines]
                if "LogConsole" in lines:
                    self.log_to_console = val
                if "LogLocation" in lines:
                    self.log_location = val
                if "LogFileWanted" in lines:
                    self.log_file_wanted = val
