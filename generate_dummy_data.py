import sqlite3
import random
import json
from datetime import datetime, date

DB_NAME = "hc_employee.db"

def generate_dummy_data(count=15):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for i in range(1, count+1):
        emp = {
            "employee_id": f"EMP{i:03}",
            "full_name": f"Dummy Employee {i}",
            "department": random.choice(["IT","Finance","Audit","HR"]),
            "last_updated": datetime.now().isoformat()
        }

        cur.execute("""
            INSERT INTO employees (employee_id, full_name, department, last_updated)
            VALUES (?,?,?,?)
        """, (emp["employee_id"], emp["full_name"], emp["department"], emp["last_updated"]))

        cur.execute("""
            INSERT INTO audit_log (action_time, user_role, action_type, employee_id,
                                   detail, before_data, after_data, ip_address)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            datetime.now().isoformat(),
            "SYSTEM",
            "INSERT_DUMMY",
            emp["employee_id"],
            "dummy-data",
            None,
            json.dumps(emp),
            "127.0.0.1"
        ))

    conn.commit()
    conn.close()
    return f"{count} dummy employees generated."
