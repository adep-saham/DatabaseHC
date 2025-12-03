import sqlite3

DB_NAME = "hc_employee.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # === TABLE: employees ===
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            department TEXT,
            bureau TEXT,
            job_title TEXT,
            mpl_level TEXT,
            work_location TEXT,
            date_joined TEXT,
            years_in_bureau REAL,
            years_in_department REAL,
            avg_perf_3yr REAL,
            has_discipline_issue INTEGER,
            technical_skills TEXT,
            soft_skills TEXT,
            certifications TEXT,
            notes TEXT,
            is_candidate_bureau_head INTEGER,
            data_quality_score REAL,
            last_updated TEXT
        )
    """)

    # === TABLE: audit_log ===
    cur.execute("""
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
