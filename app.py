import streamlit as st

from db import init_db
from ui_form import render_form
from ui_screening import render_screening
from ui_audit import render_audit
from ui_quality import render_quality
from generate_dummy_data import generate_dummy_data


# =====================================
# Add Migration Function Here
# =====================================
import sqlite3

def upgrade_audit_table():
    conn = sqlite3.connect("hc_employee.db")
    cur = conn.cursor()

    alter_sql = [
        "ALTER TABLE audit_log ADD COLUMN before_data TEXT",
        "ALTER TABLE audit_log ADD COLUMN after_data TEXT",
        "ALTER TABLE audit_log ADD COLUMN ip_address TEXT"
    ]

    results = []
    for sql in alter_sql:
        try:
            cur.execute(sql)
            results.append(f"✔ SUCCESS: {sql}")
        except Exception as e:
            results.append(f"⚠ SKIPPED: {sql} — {e}")

    conn.commit()
    conn.close()
    return results


def force_rebuild_audit_log():
    conn = sqlite3.connect("hc_employee.db")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS audit_log_old;")
    cur.execute("ALTER TABLE audit_log RENAME TO audit_log_old;")

    cur.execute("""
    CREATE TABLE audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_time TEXT,
        user_role TEXT,
        action_type TEXT,
        employee_id TEXT,
        detail TEXT,
        before_data TEXT,
        after_data TEXT,
        ip_address TEXT
    );
    """)

    cur.execute("""
        INSERT INTO audit_log (action_time, user_role, action_type, employee_id, detail)
        SELECT action_time, user_role, action_type, employee_id, detail
        FROM audit_log_old;
    """)

    conn.commit()
    conn.close()

    return "🎉 Tabel audit_log berhasil direbuild total!"


# =====================================

st.set_page_config(page_title="HC Employee Database", layout="wide")

st.title("📋 HC Employee Database – HC System & Data Management")

# Init DB
init_db()

# Role selector
role = st.sidebar.selectbox(
    "Role",
    ["Viewer", "HR Admin", "HC System Bureau Head"],
    index=1
)

# Main Menu
menu = st.sidebar.radio(
    "Menu",
    [
        "Input / Update Data Pegawai",
        "Screening Kandidat",
        "Audit Trail",
        "Data Quality Dashboard"
    ]
)

# =====================================
# Add the BUTTON here
# =====================================
if role == "HC System Bureau Head":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠 SQL Console (Admin Only)")

    sql_input = st.sidebar.text_area("SQL Query", "")
    if st.sidebar.button("Run SQL"):
        try:
            import sqlite3
            conn = sqlite3.connect("hc_employee.db")
            cur = conn.cursor()
            cur.execute(sql_input)
            rows = cur.fetchall()
            conn.commit()
            conn.close()
            st.sidebar.success("Query executed!")
            st.write("### SQL Result")
            st.write(rows)
        except Exception as e:
            st.sidebar.error(str(e))

    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠 Database Tools")

    if role == "HC System Bureau Head":
        st.sidebar.markdown("---")
        if st.sidebar.button("🚨 Force Rebuild audit_log Table"):
                st.sidebar.success(force_rebuild_audit_log())

    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠 Developer Tools")

    if st.sidebar.button("🚀 Generate Dummy Data"):
        msg = generate_dummy_data(15)
        st.sidebar.success(msg)
    


# =====================================

if menu == "Input / Update Data Pegawai":
    render_form(role)

elif menu == "Screening Kandidat":
    render_screening()

elif menu == "Audit Trail":
    render_audit()

elif menu == "Data Quality Dashboard":
    render_quality()





