import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

DB_NAME = "hcis_master.db"

# ------------------------------------------------------
# DATABASE HANDLER
# ------------------------------------------------------
@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    # PERSONAL DATA
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PersonalData (
            employee_no TEXT PRIMARY KEY,
            employee_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            official_name TEXT,
            initial_name TEXT,
            salutation TEXT,
            education_title_1 TEXT,
            education_title_2 TEXT,
            nationality TEXT,
            id_number TEXT,
            id_expiry_date TEXT,
            birth_place TEXT,
            birth_date TEXT,
            gender TEXT,
            religion TEXT,
            race TEXT,
            dialect TEXT,
            marital_status TEXT,
            marital_place TEXT,
            marital_date TEXT,
            tax_registered_name TEXT,
            tax_file_number TEXT
        )
    """)

    # ADDRESS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Address (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_no TEXT,
            address_type TEXT,
            address TEXT,
            map TEXT,
            city TEXT,
            state_province TEXT,
            phone TEXT
        )
    """)

    # EMPLOYMENT INFO
    cur.execute("""
        CREATE TABLE IF NOT EXISTS EmploymentInfo (
            employee_no TEXT PRIMARY KEY,
            join_date TEXT,
            terminate_date TEXT,
            employment_end_date TEXT,
            employment_status TEXT,
            current_position TEXT,
            job_status TEXT,
            person_grade TEXT,
            job_grade TEXT,
            physical_location TEXT,
            cost_center TEXT,
            employee_status TEXT,
            direct_supervisor TEXT,
            immediate_manager TEXT
        )
    """)

    # EMPLOYEE LEAVE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS EmployeeLeave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_no TEXT,
            type_of_leave TEXT,
            given_leave_period REAL,
            start_date TEXT,
            end_date TEXT,
            leave_quota REAL,
            proportional REAL,
            bring_forward REAL,
            forfeited REAL,
            adjustment REAL,
            used REAL,
            remaining_leave REAL,
            active_status TEXT
        )
    """)

    # TRAINING RECORD
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TrainingRecord (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_no TEXT,
            training_no TEXT,
            event_type TEXT,
            training_course TEXT,
            start_date TEXT,
            end_date TEXT
        )
    """)

    # AUDIT LOG
    cur.execute("""
        CREATE TABLE IF NOT EXISTS AuditLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_time TEXT,
            sheet_name TEXT,
            record_count INTEGER
        )
    """)

    conn.commit()

def log(sheet, count):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO AuditLog (action_time, sheet_name, record_count)
        VALUES (?, ?, ?)
    """, (datetime.now().isoformat(timespec="seconds"), sheet, count))
    conn.commit()

# Initialize DB
init_db()


# ------------------------------------------------------
# UI START
# ------------------------------------------------------
st.title("📥 HCIS Master Data Import (Excel Version)")
st.caption("Upload file: HCIS_Master_Template.xlsx")


uploaded = st.file_uploader("Upload Excel Master Template", type=["xlsx"])

if uploaded:

    st.success("File berhasil diupload. Membaca isi Excel...")

    xls = pd.ExcelFile(uploaded)

    sheets = ["PersonalData","Address","EmploymentInfo","EmployeeLeave","TrainingRecord"]

    conn = get_conn()
    cur = conn.cursor()

    for sheet in sheets:

        if sheet not in xls.sheet_names:
            st.error(f"Sheet '{sheet}' tidak ditemukan.")
            st.stop()

        df = pd.read_excel(uploaded, sheet_name=sheet)

        st.subheader(f"📑 {sheet} — {len(df)} record")
        st.dataframe(df, use_container_width=True)

        # Insert to DB
        for _, row in df.iterrows():
            cols = ",".join(row.index)
            qs = ",".join(["?"] * len(row.index))

            cur.execute(f"""
                INSERT OR REPLACE INTO {sheet} ({cols})
                VALUES ({qs})
            """, tuple(row.values))

        conn.commit()
        log(sheet, len(df))

    st.success("🎉 Semua sheet berhasil diimport ke database.")


# ------------------------------------------------------
# SHOW DATABASE CONTENT
# ------------------------------------------------------
st.header("📚 Database Preview")

conn = get_conn()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "PersonalData","Address","EmploymentInfo",
    "EmployeeLeave","TrainingRecord","AuditLog"
])

with tab1:
    df = pd.read_sql("SELECT * FROM PersonalData", conn)
    st.dataframe(df, use_container_width=True)

with tab2:
    df = pd.read_sql("SELECT * FROM Address", conn)
    st.dataframe(df, use_container_width=True)

with tab3:
    df = pd.read_sql("SELECT * FROM EmploymentInfo", conn)
    st.dataframe(df, use_container_width=True)

with tab4:
    df = pd.read_sql("SELECT * FROM EmployeeLeave", conn)
    st.dataframe(df, use_container_width=True)

with tab5:
    df = pd.read_sql("SELECT * FROM TrainingRecord", conn)
    st.dataframe(df, use_container_width=True)

with tab6:
    df = pd.read_sql("SELECT * FROM AuditLog ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)
