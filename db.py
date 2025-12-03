import sqlite3
import streamlit as st
from datetime import datetime

@st.cache_resource
def get_conn():
    return sqlite3.connect("hc_employee.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
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

def fetch_employee(emp_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE employee_id=?", (emp_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    return dict(zip(cols, row))

def fetch_all_employee_ids():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT employee_id FROM employees ORDER BY employee_id")
    return [r[0] for r in cur.fetchall()]
