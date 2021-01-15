import datetime
import glob
import gzip
from os import path
from .plugin_helpers import common_file_helper


class PluginNVDRetriever:

    def __init__(self, log_manager, args):
        self.passed_args = args
        self.component_name = "PluginNVDRetriever"
        self.component_version = "0.0.0"
        self.logger = log_manager
        self.config_data_startswith = self.component_name
        self.config_data = dict()
        self.nvd_url_base = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-"
        self.nvd_url_recent = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz"
        self.nvd_url_mod = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.json.gz"
        self.data_path = None

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)
        for file in glob.glob("./**/data", recursive=True):
            if "security-tracker" in file:
                continue
            self.data_path = file

    def handle_component_config(self, data):
        for lines in data:
            if lines.startswith(self.config_data_startswith):
                val = data[lines]
                self.config_data[lines] = val

    def prepare(self):
        self.logger.log("Prepare called at " + self.component_name + " ver " + self.component_version)

    def download(self, command):
        out = "[" + self.component_name + "] Starting NVD data download"
        self.logger.log(out)
        start = int(self.config_data['PluginNVDRetrieverStartYear'])
        current_year = datetime.datetime.now().year
        for y in range(start, current_year + 1):
            download_file_to = "nvd_" + str(y) + ".json.gz"
            d_file = self.data_path + "/" + download_file_to
            url_wanted = self.nvd_url_base + str(y) + ".json.gz"
            if y == current_year:
                common_file_helper.download_file_from_to(url_wanted, d_file)
            elif not path.exists(download_file_to):
                common_file_helper.download_file_from_to(url_wanted, d_file)
        common_file_helper.download_file_from_to(self.nvd_url_recent,
                                                 self.data_path + "/" + "nvd_9999999999_recent.json.gz")
        common_file_helper.download_file_from_to(self.nvd_url_mod,
                                                 self.data_path + "/" + "nvd_9999999999_mod.json.gz")
        for file in glob.glob("./**/data/nvd*.json.gz", recursive=True):
            extract_name = file.replace("nvd", "extracted_").replace("json.gz", "json")
            if str(current_year) in file:
                common_file_helper.extract_gzip_to_file(file, extract_name)
            if not path.exists(extract_name):
                common_file_helper.extract_gzip_to_file(file, extract_name)
            if "9999999999" in file:
                common_file_helper.extract_gzip_to_file(file, extract_name)
        self.logger.log("*** Retrieve - NVD Data complete")

