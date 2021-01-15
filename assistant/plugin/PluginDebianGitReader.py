import glob
import sqlite3
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
        self.wanted_files_cve = "CVE/list"
        self.wanted_files_dla = "DLA/list"
        self.wanted_files_dsa = "DSA/list"
        self.data_cve = dict()
        self.data_dxa = dict()
        self.data_entry_template = dict()
        self.retrieved_data = dict()
        self.table_used_alerts = "parsed_data_debian_alerts"
        self.table_used_cve = "parsed_data_debian_cve"

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
        self.data_entry_template["CVE"] = dict()

    def set_database_connection(self, database_conn):
        self.database_conn = database_conn

    def refresh_database(self):
        out = "[" + self.component_name + "] Starting Debian Database Update "
        self.logger.log(out)
        self.refresh_cve()
        self.refresh_dxa()

    def refresh_cve(self):
        self.logger.log("Refresh CVE")
        db_c = self.database_conn.db_cursor
        try:
            db_c.execute('''DROP TABLE ''' + str(self.table_used_cve))
        except sqlite3.OperationalError as err:
            self.logger.log(err)
        db_c.execute('''CREATE TABLE ''' + self.table_used_cve + ''' (cve text,
                description text, s_keywords text, s_text text, reference text,
                branch text, package text, version text, fix_text text, notes text)''')
        for cve_k in self.data_cve:
            for cve_item in self.data_cve[cve_k]:
                cve = cve_item["CVE"]
                text = cve_item["CVE_TEXT"]
                keywords = cve_item["CVE_SPECIAL_KEYWORDS"]
                key_text = cve_item["CVE_SPECIAL_TEXT"]
                reference = cve_item["CVE_REFERENCE"]
                notes_all = cve_item["NOTES"]
                notes_combined = False
                for n in notes_all:
                    if not notes_combined:
                        notes_combined = n
                    else:
                        notes_combined = notes_combined + "\n" + n
                for branch in cve_item["branch"]:
                    for p in cve_item["branch"][branch]:
                        package = cve_item["branch"][branch][p]["package"]
                        version = cve_item["branch"][branch][p]["version"]
                        fix_text = cve_item["branch"][branch][p]["text"]
                        add_in = [cve, text, keywords, key_text, reference, branch, package,
                                  version, fix_text, notes_combined]
                        statement = "INSERT INTO " + self.table_used_cve + " VALUES (?,?,?,?,?,?,?,?,?,?)"
                        db_c.execute(statement, add_in)
        self.database_conn.commit_db()

    def refresh_dxa(self):
        self.logger.log("Refresh DXA")
        db_c = self.database_conn.db_cursor
        try:
            db_c.execute('''DROP TABLE ''' + str(self.table_used_alerts))
        except sqlite3.OperationalError as err:
            self.logger.log(err)
        db_c.execute('''CREATE TABLE ''' + self.table_used_alerts + ''' (date text,
                      alert_type text, alert text, description text, reference text, freeform text,
                      branch text, package text, version text)''')
        for dxa_type in self.data_dxa:
            for dxa_e in self.data_dxa[dxa_type]:
                for dxa in self.data_dxa[dxa_type][dxa_e]:
                    date = dxa["date"]
                    alert = dxa["alert"]
                    a_text = dxa["alert_text"]
                    a_reference = dxa["ALERT_REFERENCE"]
                    a_freeform = dxa["freeform"]
                    freeform = False
                    for a in a_freeform:
                        if not freeform:
                            freeform = a
                        else:
                            freeform = freeform + "\n" + a
                    for pk in dxa["package"]:
                        branch = pk["branch"]
                        package = pk["package"]
                        version = pk["version"]
                        add_in = [date, dxa_type, alert, a_text, a_reference, freeform,
                                  branch, package, version]
                        statement = "INSERT INTO " + self.table_used_alerts + " VALUES (?,?,?,?,?,?,?,?,?)"
                        db_c.execute(statement, add_in)
            self.database_conn.commit_db()
        self.database_conn.commit_db()

    def parse_data_files(self, command):
        out = "[" + self.component_name + "] Starting Debian Data Read" + str(command)
        self.logger.log(out)
        self.parse_debian_cve(self.data_path + "/" + self.wanted_files_cve)
        self.parse_debian_dxa(self.data_path + "/" + self.wanted_files_dla, "DLA")
        self.parse_debian_dxa(self.data_path + "/" + self.wanted_files_dsa, "DSA")
        self.logger.log("*** Retrieve - Debian Data read and parse complete")
        self.refresh_database()

    def parse_debian_cve(self, file_path):
        self.logger.log("Start DebianFileParseCVE " + str(file_path))
        read_cve = "\n----\nCVE-DOES-NOT-EXIST\n" + read_file_as_string(file_path)
        for cve_entries in read_cve.split("CVE-"):
            entry = dict()
            cve_key = None
            entry["CVE"] = None
            entry["CVE_TEXT"] = None
            entry["CVE_SPECIAL_KEYWORDS"] = None
            entry["CVE_SPECIAL_TEXT"] = None
            entry["CVE_REFERENCE"] = None
            entry["branch"] = dict()
            entry["branch"]["default"] = dict()
            entry["NOTES"] = []
            cve_entries = "CVE-" + cve_entries
            for lines in cve_entries.splitlines():
                if lines.startswith("\t"):
                    if lines.startswith("\t{"):
                        lines.replace("\t", "")
                        lines = replace_commas(remove_unwanted_characters(lines), ":")
                        lines = lines.replace(" ", ":")
                        entry["CVE_REFERENCE"] = lines

                    elif lines.startswith("\t["):
                        lines = lines.replace("\t[", "")
                        branch = lines.split("] - ")[0]
                        package = lines.replace(branch + "] - ", "").split(" ")[0]
                        version = lines.replace(branch + "] - ", "").replace(package + " ", "").split(" ")[0]
                        text = None
                        if "(" in lines:
                            text = "(" + lines.split("(")[1]
                        if package not in entry["branch"]["default"]:
                            entry["branch"]["default"][package] = dict()
                        entry["branch"]["default"][package]["package"] = package
                        entry["branch"]["default"][package]["version"] = version
                        entry["branch"]["default"][package]["text"] = text

                    elif lines.startswith("\t-"):
                        lines = lines.replace("\t- ", "")
                        package = lines.split(" ")[0]
                        version = lines.replace(package + " ", "").split(" ")[0]
                        text = None
                        if "(" in lines:
                            text = "(" + lines.split("(")[1]
                        if package not in entry["branch"]["default"]:
                            entry["branch"]["default"][package] = dict()
                        entry["branch"]["default"][package]["package"] = package
                        entry["branch"]["default"][package]["version"] = version
                        entry["branch"]["default"][package]["text"] = text

                    elif lines.startswith("\tNOTE:"):
                        lines = lines.replace("\t", "")
                        entry["NOTES"].append(lines)

                    elif lines.startswith("\tNOT-FOR-US:"):
                        entry["CVE_SPECIAL_KEYWORDS"] = "NOT-FOR-US"
                        entry["CVE_SPECIAL_TEXT"] = remove_unwanted_characters(lines.split("NOT-FOR-US: ")[1])

                    elif lines.startswith("\tRESERVED:"):
                        entry["CVE_SPECIAL_KEYWORDS"] = "RESERVED"

                    elif lines.startswith("\tREJECTED:"):
                        entry["CVE_SPECIAL_KEYWORDS"] = "REJECTED"
                else:
                    cve = lines.split(" ")[0]
                    cve_key = cve
                    text = lines.replace(cve + " ", "")
                    text = replace_commas(remove_unwanted_characters(text))
                    entry["CVE"] = cve
                    entry["CVE_TEXT"] = text
            if cve_key not in self.data_cve:
                self.data_cve[cve_key] = []
                self.data_cve[cve_key].append(entry)

    def parse_debian_dxa(self, file_path, type):
        self.logger.log("Start DebianFileParseDLA " + str(file_path))
        read_dxa = "\n----\n[99 NEV 9999]\n" + read_file_as_string(file_path)
        read_entries = []
        added = []
        debug_entry = "FINDME"
        if type not in self.data_dxa:
            self.data_dxa[type] = dict()
        for dxa_entries in read_dxa.split("\n["):
            dxa_entries = "[" + dxa_entries
            entry = dict()
            entry["date"] = None
            entry["alert"] = None
            entry["alert_on_package"] = None
            entry["alert_text"] = None
            entry["package"] = []
            entry["ALERT_REFERENCE"] = None
            entry["freeform"] = []
            alert_key = None
            debug_print = False
            for lines in dxa_entries.splitlines():
                if debug_entry in lines:
                    debug_print = True
                else:
                    debug_print = False
                if debug_print:
                    print("+++ Lines")
                    print(lines)
                if lines.startswith("\t"):
                    lines = lines.replace("\t", "")
                    if lines.startswith("{"):
                        entry["ALERT_REFERENCE"] = remove_unwanted_characters(lines.replace(" ", ":"))
                    elif lines.startswith("["):
                        branch = remove_unwanted_characters(lines.split("]")[0])
                        package = lines.replace(branch + "] - ", "").split(" ")[0]
                        version = lines.replace(branch + "] - ", "").replace(package + " ", "")
                        mini_add = dict()
                        mini_add["branch"] = remove_unwanted_characters(branch)
                        mini_add["package"] = remove_unwanted_characters(package)
                        mini_add["version"] = remove_unwanted_characters(version)
                        entry["package"].append(mini_add)
                    else:
                        entry["freeform"].append(lines)
                else:
                    date = lines.replace("[", "").split("] D")[0]
                    alert_key = remove_unwanted_characters(lines.replace(date + "] ", "").split(" ")[0])
                    alert_key.replace("[", "")
                    read_entries.append(remove_unwanted_characters(alert_key))
                    package = lines.replace(date + "] ", "").replace(alert_key + " ", "").split(" - ")[0]
                    text = lines.replace(date + "] ", "").replace(alert_key + " ", "").replace(package + " ", "")
                    entry["date"] = remove_unwanted_characters(date)
                    entry["alert"] = remove_unwanted_characters(alert_key)
                    entry["alert_on_package"] = remove_unwanted_characters(package)
                    entry["alert_text"] = remove_unwanted_characters(text.replace("- ", ""))
            if alert_key not in self.data_dxa[type]:
                self.data_dxa[type][alert_key] = []
            self.data_dxa[type][alert_key].append(entry)
            added.append(alert_key)
            if debug_entry == alert_key:
                print("Debug Entry?")
                print(self.data_dxa[type][alert_key])
