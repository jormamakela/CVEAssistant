import glob
from .plugin_helpers.common_file_helper import *


class PluginDebianGitReader:

    def __init__(self, log_manager, args):
        self.component_name = "PluginDebianGitReader"
        self.component_version = "0.0.0"
        self.logger = log_manager
        self.config_data_startswith = self.component_name
        self.config_data = dict()
        self.data_path = None
        self.database_conn = None
        self.wanted_files = ["CVE/list", "DLA/list", "DSA/list"]
        self.retrieved_data = dict()

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)
        for file in glob.glob("./**/data", recursive=True):
            if "security-tracker" not in file:
                continue
            self.data_path = file

    def handle_component_config(self, data):
        for lines in data:
            if lines.startswith(self.config_data_startswith):
                val = data[lines]
                self.config_data[lines] = val

    def prepare(self):
        self.logger.log("Prepare called at " + self.component_name + " ver " + self.component_version)

    def set_database_connection(self, database_conn):
        self.database_conn = database_conn

    def refresh_database(self):
        out = "[" + self.component_name + "] Starting Debian Database Update "
        self.logger.log(self.retrieved_data)

    def parse_data_files(self, command):
        out = "[" + self.component_name + "] Starting Debian Data Read" + str(command)
        self.logger.log(out)
        for file in self.wanted_files:
            self.parse_general_debian_file(self.data_path + "/" + file)
        self.logger.log("*** Retrieve - Debian Data read and parse complete")
        self.refresh_database()

    def handle_data_file_cve(self, data):
        for cve_sets in data.split("\nCVE"):
            if len(cve_sets) < 5:
                continue
            cve_sets = "CVE" + cve_sets
            base_info_cve = None
            base_info_freeflow = None
            deb_related_ticket_info = None
            deb_branches_raw = []
            deb_packages_raw = []
            deb_keyword_data = []

            for line in cve_sets.splitlines():
                if not line.startswith("\t"):
                    base_info_cve = line.split(" ")[0]
                    base_info_freeflow = remove_unwanted_characters(line.replace(base_info_cve + " ", ""))
                    base_info_freeflow = replace_commas(base_info_freeflow)
                else:
                    if line.startswith("\t{"):
                        line = line.replace("\t{", "").replace("}", "").replace(" ", ",")
                        deb_related_ticket_info = line
                    elif line.startswith("\t-"):
                        line = line.replace("\t- ", "")
                        deb_packages_raw.append(line)
                    elif line.startswith("\t["):
                        deb_branches_raw.append(line.replace("\t", ""))
                    else:
                        deb_keyword_data.append(line.replace("\t", ""))
            if "CVE/list" not in self.retrieved_data:
                self.retrieved_data["CVE/list"] = dict()
            if base_info_cve not in self.retrieved_data["CVE/list"]:
                self.retrieved_data["CVE/list"][base_info_cve] = []
            add_dict = dict()
            add_dict["CVE"] = base_info_cve
            add_dict["info"] = base_info_freeflow
            add_dict["related"] = deb_related_ticket_info
            for deb_pkg in deb_packages_raw:
                deb_package = deb_pkg.split(" ")[0]
                deb_ver = deb_pkg.split(" ")[1]
                impacted_pkg_line = deb_package + " " + deb_ver
                for branch in deb_branches_raw:
                    branch_pkg_set = branch.split(" - ")[1]
                    branch_pkg = branch_pkg_set.split(" ")[0]
                    branch_ver = branch_pkg_set.split(" ")[1]
                    if deb_package == branch_pkg:
                        impacted_pkg_line += " " + branch.split(" - ")[0]
                        impacted_pkg_line += " " + branch_ver
                if "branch_data" not in add_dict:
                    add_dict["branch_data"] = []
                add_dict["branch_data"].append(impacted_pkg_line)
            self.retrieved_data["CVE/list"][base_info_cve].append(add_dict)

    def parse_general_debian_file(self, file):
        self.logger.log("Starting Debian Parse on file " + str(file))
        raw_file_as_string = "\nCVE\n" + read_file_as_string(file)
        if raw_file_as_string.startswith("CVE"):
            self.handle_data_file_cve(raw_file_as_string)






