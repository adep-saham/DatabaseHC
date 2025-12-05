import sqlite3
import json
from datetime import datetime
import pytz

# ============================================
# TIMEZONE WIB FIX — 100% MATCH LAPTOP USER
# ============================================
WIB = pytz.timezone("Asia/Jakarta")

def now_wib():
    return datetime.now().astimezone(WIB).isoformat(timespec="seconds")


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
                username TEXT,
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


    # =====================================================
    # INTERNAL WRITE DB FUNCTION
    # =====================================================
    def _write_db_log(self, action_time, username, user_role,
                      action_type, employee_id, detail, before, after, ip):

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO audit_log
            (action_time, username, user_role, action_type,
             employee_id, detail, before_data, after_data, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            action_time,
            username,
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


    # =====================================================
    # INSERT LOG
    # =====================================================
    def log_insert(self, username, user_role, employee_id, after, ip="0.0.0.0"):
        action_time = now_wib()

        self._write_db_log(
            action_time, username, user_role,
            "INSERT", employee_id, "Insert employee",
            {}, after, ip
        )


    # =====================================================
    # UPDATE LOG
    # =====================================================
    def log_update(self, username, user_role, employee_id, before, after, ip="0.0.0.0"):
        action_time = now_wib()

        detail = json.dumps({
            k: {"before": before[k], "after": after[k]}
            for k in after if k in before and before[k] != after[k]
        }, ensure_ascii=False)

        self._write_db_log(
            action_time, username, user_role,
            "UPDATE", employee_id, detail,
            before, after, ip
        )
