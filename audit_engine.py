# audit_engine.py
# =========================================================
# Audit Trail Engine (Modular Version)
# =========================================================

import sqlite3
from datetime import datetime
import json
import os


class AuditTrail:
    def __init__(self, db_path="hc_employee.db", logfile="audit_log.txt"):
        self.db_path = db_path
        self.logfile = logfile
        self._init_table()

    # =====================================================
    # INIT DATABASE TABLE
    # =====================================================
    def _init_table(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_time TEXT,
                user_role TEXT,
                action_type TEXT,
                employee_id TEXT,
                detail TEXT,
                before_data TEXT,
                after_data TEXT,
                ip_address TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================
    def _write_file_log(self, entry):
        """Append log ke audit_log.txt"""
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def _write_db_log(self, action_type, user_role, employee_id, detail, before, after, ip):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO audit_log
            (action_time, user_role, action_type, employee_id, detail, before_data, after_data, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                user_role,
                action_type,
                employee_id,
                json.dumps(before, ensure_ascii=False),
                json.dumps(after, ensure_ascii=False),
                ip,
                detail,
            ),
        )

        conn.commit()
        conn.close()

    # =====================================================
    # LOGGING METHODS
    # =====================================================
    def log_access(self, user_role, action, ip="0.0.0.0"):
        entry = f"[{datetime.now()}] ACCESS | User={user_role} | Action={action} | IP={ip}"
        self._write_file_log(entry)
        self._write_db_log("ACCESS", user_role, "-", action, None, None, ip)

    def log_insert(self, user_role, employee_id, new_data, ip="0.0.0.0"):
        entry = (
            f"[{datetime.now()}] INSERT | User={user_role} | EmpID={employee_id} "
            f"| After={new_data} | IP={ip}"
        )
        self._write_file_log(entry)
        self._write_db_log("INSERT", user_role, employee_id, "Insert new employee", None, new_data, ip)

    def log_delete(self, user_role, employee_id, old_data, ip="0.0.0.0"):
        entry = (
            f"[{datetime.now()}] DELETE | User={user_role} | EmpID={employee_id} "
            f"| Before={old_data} | IP={ip}"
        )
        self._write_file_log(entry)
        self._write_db_log("DELETE", user_role, employee_id, "Delete employee", old_data, None, ip)

    def log_update(self, user_role, employee_id, before, after, ip="0.0.0.0"):
        """Bandingkan perubahan field-level otomatis"""
        changes = {}

        for key in after:
            if key in before and before[key] != after[key]:
                changes[key] = {"before": before[key], "after": after[key]}

        detail_msg = f"Field changes: {json.dumps(changes, ensure_ascii=False)}"

        entry = (
            f"[{datetime.now()}] UPDATE | User={user_role} | EmpID={employee_id} "
            f"| Changes={changes} | IP={ip}"
        )

        self._write_file_log(entry)
        self._write_db_log("UPDATE", user_role, employee_id, detail_msg, before, after, ip)

    # Getter untuk digunakan oleh Streamlit
    def get_logs_df(self):
        import pandas as pd

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)
        conn.close()
        return df
