import streamlit as st
from datetime import datetime
from db import get_conn
from audit_engine import AuditTrail

audit_engine = AuditTrail()

# ============================================
# SAFE VALUE HANDLERS
# ============================================
def safe_int(x):
    try:
        if x is None:
            return 0
        return int(float(x))
    except:
        return 0

def safe_float(x):
    try:
        if x is None:
            return 0.0
        return float(x)
    except:
        return 0.0


# ============================================
# FORM UTAMA
# ============================================
def render_form(role, username):

    st.subheader("📄 Input / Update Data Pegawai")

    conn = get_conn()
    cur = conn.cursor()

    # ==========================
    # LOAD EMPLOYEE IDs
    # ==========================
    cur.execute("SELECT employee_id FROM employees")
    emp_ids = [r[0] for r in cur.fetchall()]

    mode = st.selectbox("Mode", ["Tambah Baru"] + emp_ids)
    editing = mode != "Tambah Baru"

    # ==========================
    # LOAD OLD DATA IF EDITING
    # ==========================
    if editing:
        cur.execute("SELECT * FROM employees WHERE employee_id=?", (mode,))
        col = [d[0] for d in cur.description]
        row_db = cur.fetchone()
        old = dict(zip(col, row_db))
    else:
        old = {}

    # ============================================
    # FIELD DASAR
    # ============================================
    employee_id = st.text_input("Employee ID", value=old.get("employee_id", ""), disabled=editing)
    full_name = st.text_input("Nama", value=old.get("full_name", ""))
    department = st.text_input("Department", value=old.get("department", ""))

    # ============================================
    # ADVANCED DETAILS
    # ============================================
    with st.expander("Advanced Details"):

        bureau = st.text_input("Bureau", value=old.get("bureau", ""))
        job_title = st.text_input("Job Title", value=old.get("job_title", ""))
        work_location = st.text_input("Work Location", value=old.get("work_location", ""))
        mpl_level = st.text_input("MPL Level", value=old.get("mpl_level", ""))

        years_in_bureau = st.number_input(
            "Years in Bureau",
            min_value=0, max_value=80,
            value=safe_int(old.get("years_in_bureau"))
        )

        years_in_department = st.number_input(
            "Years in Department",
            min_value=0, max_value=80,
            value=safe_int(old.get("years_in_department"))
        )

        avg_perf_3yr = st.number_input(
            "Rata-rata Kinerja 3 Tahun",
            min_value=0.0, max_value=5.0, step=0.1,
            value=safe_float(old.get("avg_perf_3yr"))
        )

        technical_skills = st.text_area("Technical Skills (pisahkan dengan koma)", 
                                        value=old.get("technical_skills", ""))

        soft_skills = st.text_area("Soft Skills (pisahkan dengan koma)", 
                                   value=old.get("soft_skills", ""))

        certifications = st.text_area("Certifications (pisahkan dengan koma)", 
                                      value=old.get("certifications", ""))

        has_discipline_issue = st.checkbox(
            "Memiliki Catatan Disiplin?",
            value=bool(old.get("has_discipline_issue")) if editing else False
        )


    # ============================================
    # SIMPAN BUTTON
    # ============================================
    if st.button("💾 SIMPAN"):

        new_data = {
            "employee_id": employee_id,
            "full_name": full_name,
            "department": department,
            "bureau": bureau,
            "job_title": job_title,
            "work_location": work_location,
            "mpl_level": mpl_level,
            "years_in_bureau": years_in_bureau,
            "years_in_department": years_in_department,
            "avg_perf_3yr": avg_perf_3yr,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "certifications": certifications,
            "has_discipline_issue": int(has_discipline_issue),
            "last_updated": datetime.now().isoformat()
        }

        # ============================================
        # UPDATE EXISTING EMPLOYEE
        # ============================================
        if editing:

            cur.execute("""
                UPDATE employees SET 
                    full_name=?, department=?, bureau=?, job_title=?,
                    work_location=?, mpl_level=?, years_in_bureau=?, 
                    years_in_department=?, avg_perf_3yr=?, technical_skills=?,
                    soft_skills=?, certifications=?, has_discipline_issue=?,
                    last_updated=?
                WHERE employee_id=?
            """, (
                full_name, department, bureau, job_title,
                work_location, mpl_level, years_in_bureau,
                years_in_department, avg_perf_3yr, technical_skills,
                soft_skills, certifications, int(has_discipline_issue),
                new_data["last_updated"], employee_id
            ))

            conn.commit()

            audit_engine.log_update(username, role, employee_id, old, new_data)
            st.success("Data berhasil di-update!")

        # ============================================
        # INSERT NEW EMPLOYEE
        # ============================================
        else:
            cur.execute("""
                INSERT INTO employees (
                    employee_id, full_name, department, bureau, job_title, work_location,
                    mpl_level, years_in_bureau, years_in_department, avg_perf_3yr,
                    technical_skills, soft_skills, certifications, has_discipline_issue,
                    last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee_id, full_name, department, bureau, job_title, work_location,
                mpl_level, years_in_bureau, years_in_department, avg_perf_3yr,
                technical_skills, soft_skills, certifications, int(has_discipline_issue),
                new_data["last_updated"]
            ))

            conn.commit()

            audit_engine.log_insert(username, role, employee_id, new_data)
            st.success("Pegawai baru berhasil ditambahkan!")

    conn.close()
