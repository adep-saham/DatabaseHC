# audit_engine.py
# =========================================================
# Audit Trail Engine (Final, Stable Version)
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

    # -----------------------------------------------------
    # INIT TABLE
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # LOW LEVEL WRITERS
    # -----------------------------------------------------
    def _write_file_log(self, entry: str):
        """Tulis log ke file teks (opsional, untuk debugging/audit offline)."""
        try:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception:
            # jangan sampai gagal hanya gara-gara file log
            pass

    def _write_db_log(
        self,
        action_type: str,
        user_role: str,
        employee_id: str,
        detail: str,
        before: dict,
        after: dict,
        ip: str,
    ):
        """Tulis log ke tabel audit_log (INI YANG DIPAKAI UI)."""

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO audit_log
            (action_time, user_role, action_type, employee_id, detail,
             before_data, after_data, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                user_role,
                action_type,
                employee_id,
                detail,
                json.dumps(before, ensure_ascii=False),
                json.dumps(after, ensure_ascii=False),
                ip,
            ),
        )

        conn.commit()
        conn.close()

    # -----------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------
    def log_insert(self, user_role: str, employee_id: str, after: dict, ip: str = "0.0.0.0"):
        """Log ketika insert karyawan baru."""
        detail_msg = "INSERT employee data"

        entry = (
            f"[{datetime.now()}] INSERT | User={user_role} | EmpID={employee_id} "
            f"| IP={ip}"
        )

        self._write_file_log(entry)
        self._write_db_log("INSERT", user_role, employee_id, detail_msg, {}, after, ip)

    def log_update(
        self,
        user_role: str,
        employee_id: str,
        before: dict,
        after: dict,
        ip: str = "0.0.0.0",
    ):
        """Log ketika update karyawan (before vs after)."""

        # Bangun ringkasan perubahan untuk kolom yang memang berubah
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

    def log_delete(self, user_role: str, employee_id: str, before: dict, ip: str = "0.0.0.0"):
        """Opsional: log delete jika nanti dipakai."""
        detail_msg = "DELETE employee data"

        entry = (
            f"[{datetime.now()}] DELETE | User={user_role} | EmpID={employee_id} "
            f"| IP={ip}"
        )

        self._write_file_log(entry)
        self._write_db_log("DELETE", user_role, employee_id, detail_msg, before, {}, ip)

    # Getter utk kalau mau dipakai langsung dari Streamlit
    def get_logs_df(self):
        import pandas as pd

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)
        conn.close()
        return df
