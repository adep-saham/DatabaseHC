import streamlit as st
from datetime import datetime
from db import get_conn
from audit_engine import AuditTrail

audit_engine = AuditTrail()

def render_form(role, username):

    st.subheader("📄 Input / Update Data Pegawai")

    conn = get_conn()
    cur = conn.cursor()

    # Ambil daftar employee_id
    cur.execute("SELECT employee_id FROM employees")
    emp_ids = [r[0] for r in cur.fetchall()]

    mode = st.selectbox("Mode", ["Tambah Baru"] + emp_ids)
    editing = mode != "Tambah Baru"

    if editing:
        cur.execute("SELECT * FROM employees WHERE employee_id=?", (mode,))
        col = [d[0] for d in cur.description]
        old = dict(zip(col, cur.fetchone()))
    else:
        old = {}

    employee_id = st.text_input("Employee ID", value=old.get("employee_id", ""), disabled=editing)
    full_name = st.text_input("Nama", value=old.get("full_name", ""))
    department = st.text_input("Department", value=old.get("department", ""))

    if st.button("💾 SIMPAN"):

        row = {
            "employee_id": employee_id,
            "full_name": full_name,
            "department": department,
            "last_updated": datetime.now().isoformat()
        }

        # UPDATE DATA
        if editing:
            cur.execute("""
                UPDATE employees
                SET full_name=?, department=?, last_updated=?
                WHERE employee_id=?
            """, (full_name, department, row["last_updated"], employee_id))
            conn.commit()

            audit_engine.log_update(username, role, employee_id, old, row)
            st.success("Data berhasil di-update!")

        # INSERT DATA BARU
        else:
            cur.execute("""
                INSERT INTO employees (employee_id, full_name, department, last_updated)
                VALUES (?, ?, ?, ?)
            """, (employee_id, full_name, department, row["last_updated"]))
            conn.commit()

            audit_engine.log_insert(username, role, employee_id, row)
            st.success("Pegawai baru ditambahkan!")

    conn.close()
