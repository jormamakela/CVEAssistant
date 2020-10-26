import sys


class TextUserInterface:

    def __init__(self, log_manager, args):
        self.ui_root = None
        self.passed_args = args
        self.component_name = "TextUserInterface"
        self.component_version = "0.0.0"
        self.logger = log_manager

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)
