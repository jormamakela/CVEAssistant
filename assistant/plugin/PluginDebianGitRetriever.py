import git
import glob
from git import Repo


class PluginDebianGitRetriever:

    def __init__(self, log_manager, args):
        self.component_name = "PluginDebianGitRetriever"
        self.component_version = "0.0.0"
        self.logger = log_manager
        self.config_data_startswith = self.component_name
        self.config_data = dict()
        self.deb_git_url = "https://salsa.debian.org/security-tracker-team/security-tracker.git"
        self.data_path = None

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)
        for file in glob.glob("./**/data", recursive=True):
            self.data_path = file

    def download(self, command):
        out = "[" + self.component_name + "] Starting Debian Security Git download"
        self.logger.log(out)
        rel_path = None
        for file in glob.glob("./**/data/security-tracker", recursive=True):
            self.logger.log("+++ Debian security tracker at " + str(file))
            rel_path = file
        if not rel_path:
            self.logger.log("*** Creating new Debian Git Path Fetch")
            git.Git(self.data_path).clone(self.deb_git_url)
        else:
            self.logger.log("*** Fetching updates to " + str(rel_path))
            git.Repo.init(rel_path).remote().pull()
        self.logger.log("*** Retrieve - Debian Security Git complete")

    def handle_component_config(self, data):
        for lines in data:
            if lines.startswith(self.config_data_startswith):
                val = data[lines]
                self.config_data[lines] = val

    def prepare(self):
        self.logger.log("Prepare called at " + self.component_name + " ver " + self.component_version)
