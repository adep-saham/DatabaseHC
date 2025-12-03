import streamlit as st

from db import init_db
from ui_form import render_form
from ui_screening import render_screening
from ui_audit import render_audit
from ui_quality import render_quality

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
    st.sidebar.subheader("🛠 System Tools")

    if st.sidebar.button("🔧 Upgrade Audit Table"):
        st.sidebar.write("Running migration...")
        results = upgrade_audit_table()
        for r in results:
            st.sidebar.write(r)
        st.sidebar.success("Done! Database updated.")

# =====================================

if menu == "Input / Update Data Pegawai":
    render_form(role)

elif menu == "Screening Kandidat":
    render_screening()

elif menu == "Audit Trail":
    render_audit()

elif menu == "Data Quality Dashboard":
    render_quality()
