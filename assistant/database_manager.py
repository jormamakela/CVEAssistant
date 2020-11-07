import sqlite3
import glob


class DatabaseManager:

    def __init__(self, log_manager):
        self.component_name = "DatabaseManager"
        self.component_version = "0.0.0"
        self.logger = log_manager
        self.database_path_base = None
        self.database_file_name = "db.sql3"
        self.db_full_path = None
        self.db_conn = None
        self.db_cursor = None

    def go(self):
        self.logger.log("Go called at " + self.component_name + " ver " + self.component_version)
        for rel_path in glob.glob("./**/data", recursive=True):
            if "security-tracker" in rel_path:
                continue
            self.database_path_base = rel_path
        self.db_full_path = self.database_path_base + "/" + self.database_file_name
        self.logger.log("Relative database path found at ... " + self.db_full_path)
        self.prepare_cursor_and_conn()

    def prepare_cursor_and_conn(self):
        self.db_conn = sqlite3.connect(self.db_full_path)
        self.db_cursor = self.db_conn.cursor()

    def commit_db(self):
        self.db_conn.commit()

    def close_db(self):
        if self.db_conn:
            self.db_conn.commit()
            self.db_cursor.close()
