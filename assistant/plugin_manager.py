import sys


class PluginManager:

    def __init__(self, args):
        self.ui_root = None
        self.passed_args = args
        self.component_name = "PluginManager"
        self.component_version = "0.0.0"

    def go(self):
        print("Go called at " + self.component_name + " ver " + self.component_version)