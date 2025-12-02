import sqlite3
from datetime import datetime
import json

# koneksi database
def get_conn():
    return sqlite3.connect("hc_employee.db", check_same_thread=False)


# ============================
# LOG INSERT
# ============================
def log_insert(user_role, employee_id, detail="INSERT operation"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_log (action_time, user_role, action_type, employee_id, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            user_role,
            "INSERT",
            employee_id,
            detail,
        ),
    )
    conn.commit()
    conn.close()


# ============================
# LOG UPDATE (BEFORE–AFTER)
# ============================
def log_update(user_role, employee_id, before, after):
    conn = get_conn()
    cur = conn.cursor()

    diff = {}
    for key in after:
        if key in before and before[key] != after[key]:
            diff[key] = {
                "before": before[key],
                "after": after[key]
            }

    detail = json.dumps(diff, ensure_ascii=False)

    cur.execute(
        """
        INSERT INTO audit_log (action_time, user_role, action_type, employee_id, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            user_role,
            "UPDATE",
            employee_id,
            detail,
        ),
    )
    conn.commit()
    conn.close()


# ============================
# LOG DELETE (opsional)
# ============================
def log_delete(user_role, employee_id, detail="DELETE operation"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_log (action_time, user_role, action_type, employee_id, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            user_role,
            "DELETE",
            employee_id,
            detail,
        ),
    )
    conn.commit()
    conn.close()
