from .plugin_helpers.common_file_helper import *
import glob
import sqlite3


class PluginNVDReader:

    def __init__(self, log_manager, args):
        self.passed_args = args
        self.component_name = "PluginNVDReader"
        self.component_version = "0.0.0"
        self.logger = log_manager
        self.config_data_startswith = self.component_name
        self.config_data = dict()
        self.data_files = []
        self.database_conn = None
        self.retrieved_stored_data = []
        self.table_used = "parsed_data_nvd"

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)
        for file in glob.glob("./**/data/*extracted*.json", recursive=True):
            if "security-tracker" in file:
                continue
            self.data_files.append(file)

    def handle_component_config(self, data):
        for lines in data:
            if lines.startswith(self.config_data_startswith):
                val = data[lines]
                self.config_data[lines] = val

    def prepare(self):
        self.logger.log("Prepare called at " + self.component_name + " ver " + self.component_version)

    def read_data_file(self, file):
        self.logger.log("Preparing NVD file parse for " + str(file))
        json_data = parse_json_file(file)
        return make_raw_json_text_to_dict(json_data)

    def parse_data_files(self, command):
        out = "[" + self.component_name + "] Starting NVD Data Read" + str(command)
        self.logger.log(out)
        for file in self.data_files:
            self.retrieved_stored_data += self.read_data_file(file)
        self.logger.log("*** Retrieve - NVD Data read and parse complete")
        self.refresh_database()

    def set_database_connection(self, database_conn):
        self.database_conn = database_conn

    def refresh_database(self):
        out = "[" + self.component_name + "] Starting NVD Database Update"
        self.logger.log(out)
        db_c = self.database_conn.db_cursor
        try:
            db_c.execute('''DROP TABLE ''' + str(self.table_used))
        except sqlite3.OperationalError as err:
            self.logger.log(err)
        db_c.execute('''CREATE TABLE ''' + self.table_used + ''' (cve text,
         description text, urls text, cvssv3 text, cvssv2 text)''')
        for add_data in self.retrieved_stored_data:
            cve = add_data["CVE"]
            urls = add_data["URLS"]
            cvssv3 = add_data["cvssv3"]
            cvssv2 = add_data["cvssv2"]
            description = add_data["description"]
            add_in = [cve, description, urls, cvssv3, cvssv2]
            statement = "INSERT INTO " + self.table_used + " VALUES (?,?,?,?,?)"
            db_c.execute(statement, add_in)
        self.database_conn.commit_db()
        self.logger.log(out)


def make_raw_json_text_to_dict(raw):
    ret_list = []
    for cve_items in raw["CVE_Items"]:
        cve_id = cve_items["cve"]["CVE_data_meta"]["ID"]
        description = replace_commas(get_english_description(cve_items["cve"]["description"]))
        urls_raw = replace_commas(get_reference_urls(cve_items["cve"]["references"]), "|")
        cvssv3 = replace_commas(get_cvss_v3(cve_items["impact"]), "|")
        cvssv2 = replace_commas(get_cvss_v2(cve_items["impact"]), "|")
        add_me = {}
        add_me["CVE"] = cve_id
        add_me["URLS"] = urls_raw
        add_me["cvssv3"] = cvssv3
        add_me["cvssv2"] = cvssv2
        add_me["description"] = description
        ret_list.append(add_me)
    return ret_list


def get_english_description(segment):
    out = "NODESCRIPTION"
    for e in segment["description_data"]:
        if "en" in e["lang"]:
            out = e["value"]
    return out


def get_reference_urls(segment):
    out = None
    for e in segment["reference_data"]:
        if out is None:
            out = e["url"]
        else:
            out += "," + e["url"]
    if out is None:
        out = "NOREFERENCEURLS"
    return out


def get_cvss_v3(segment):
    out = "NOCVSSV3"
    if "baseMetricV3" in segment:
        base = segment["baseMetricV3"]
        out = "CVSS3:" + str(base["cvssV3"]["baseScore"])
        out += "," + base["cvssV3"]["vectorString"]
        if "userInteractionRequired" in base:
            out += "," + "USERINTERACTION:" + str(base["userInteractionRequired"])
        elif "userInteraction" in base:
            out += "," + "USERINTERACTION:" + str(base["userInteraction"])
    return out


def get_cvss_v2(segment):
    out = "NOCVSSV2"
    if "baseMetricV2" in segment:
        base = segment["baseMetricV2"]
        out = "CVSS2:" + str(base["cvssV2"]["baseScore"])
        out += "," + base["cvssV2"]["vectorString"]
        if "userInteractionRequired" in base:
            out += "," + "USERINTERACTION:" + str(base["userInteractionRequired"])
        elif "userInteraction" in base:
            out += "," + "USERINTERACTION:" + str(base["userInteraction"])
    return out
