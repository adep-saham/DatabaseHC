import sqlite3
import json
from datetime import datetime

class AuditTrail:
    def __init__(self, db_path="hc_employee.db", logfile="audit_log.txt"):
        self.db_path = db_path
        self.logfile = logfile
        self._init_table()

    def _init_table(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
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
        """)
        conn.commit()
        conn.close()

    def _write_db_log(self, action_type, user_role, employee_id, detail, before, after, ip):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO audit_log
            (action_time, user_role, action_type, employee_id, detail,
             before_data, after_data, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            user_role,
            action_type,
            employee_id,
            detail,
            json.dumps(before, ensure_ascii=False),
            json.dumps(after, ensure_ascii=False),
            ip
        ))

        conn.commit()
        conn.close()

    def log_insert(self, user_role, employee_id, after, ip="0.0.0.0"):
        self._write_db_log("INSERT", user_role, employee_id, "Insert employee", {}, after, ip)

    def log_update(self, user_role, employee_id, before, after, ip="0.0.0.0"):
        detail = json.dumps({
            k: {"before": before[k], "after": after[k]}
            for k in after if k in before and before[k] != after[k]
        }, ensure_ascii=False)

        self._write_db_log("UPDATE", user_role, employee_id, detail, before, after, ip)
