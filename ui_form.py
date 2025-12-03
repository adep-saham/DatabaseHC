import streamlit as st
from datetime import datetime, date
from db import get_conn, fetch_employee, fetch_all_employee_ids
from utils import calculate_data_quality, is_candidate_bureau_head
from audit_engine import AuditTrail

audit_engine = AuditTrail()

def render_form(user_role):

    st.subheader("🧾 Input / Update Data Pegawai")

    if user_role == "Viewer":
        st.error("Role Viewer tidak bisa mengubah data.")
        return

    # ============================
    # GET LIST PEGAWAI
    # ============================
    emp_ids = fetch_all_employee_ids()

    mode = st.selectbox(
        "Mode:",
        ["(Tambah Baru)"] + emp_ids,
        help="Pilih Employee ID untuk mengedit data lama"
    )

    editing = mode != "(Tambah Baru)"
    old = fetch_employee(mode) if editing else None

    # Helper untuk default value
    def val(field, default=""):
        if not editing:
            return default
        v = old.get(field)
        return v if v is not None else default

    # Konversi date lama
    def parse_date(x):
        try:
            return datetime.strptime(x, "%Y-%m-%d").date()
        except:
            return date.today()

    # ============================
    # FORM INPUT
    # ============================
    with st.form("employee_form"):
        col1, col2 = st.columns(2)

        with col1:
            emp_id = st.text_input(
                "Employee ID",
                value=val("employee_id"),
                disabled=editing  # tidak bisa diubah saat update
            )
            full_name = st.text_input("Nama Lengkap", value=val("full_name"))
            email = st.text_input("Email", value=val("email"))
            department = st.text_input("Department", value=val("department"))
            bureau = st.text_input("Bureau", value=val("bureau"))
            job = st.text_input("Job Title", value=val("job_title"))
            mpl = st.text_input("MPL Level", value=val("mpl_level"))
            loc = st.text_input("Lokasi Kerja", value=val("work_location"))

        with col2:
            djoin = st.date_input(
                "Tanggal Masuk",
                value=parse_date(val("date_joined", date.today().isoformat()))
            )
            thnb = st.number_input("Tahun di Bureau", min_value=0.0, max_value=50.0,
                                   value=float(val("years_in_bureau", 0)))
            thnd = st.number_input("Tahun di Dept", min_value=0.0, max_value=50.0,
                                   value=float(val("years_in_department", 0)))
            perf = st.number_input("Rata2 Kinerja 3th", min_value=0.0, max_value=5.0,
                                   value=float(val("avg_perf_3yr", 0)))
            disc = st.checkbox("Ada catatan disiplin?", value=bool(val("has_discipline_issue", False)))

        st.markdown("### Kompetensi")
        tech = st.text_area("Technical Skills", value=val("technical_skills"))
        softs = st.text_area("Soft Skills", value=val("soft_skills"))
        cert = st.text_area("Certifications", value=val("certifications"))
        notes = st.text_area("Catatan", value=val("notes"))

        submit = st.form_submit_button("💾 Simpan Data")

    # Tidak submit → stop
    if not submit:
        return

    # ============================
    # PERSIST DATA
    # ============================
    row = {
        "employee_id": emp_id,
        "full_name": full_name,
        "email": email,
        "department": department,
        "bureau": bureau,
        "job_title": job,
        "mpl_level": mpl,
        "work_location": loc,
        "date_joined": djoin.isoformat(),
        "years_in_bureau": thnb,
        "years_in_department": thnd,
        "avg_perf_3yr": perf,
        "has_discipline_issue": 1 if disc else 0,
        "technical_skills": tech,
        "soft_skills": softs,
        "certifications": cert,
        "notes": notes,
    }

    row["data_quality_score"] = calculate_data_quality(row)
    row["is_candidate_bureau_head"] = 1 if is_candidate_bureau_head(row) else 0
    row["last_updated"] = datetime.now().isoformat(timespec="seconds")

    conn = get_conn()
    cur = conn.cursor()

    # ============================
    # UPDATE MODE
    # ============================
    if editing:
        before = old
        after = row

        cur.execute("""
            UPDATE employees SET
                full_name=?, email=?, department=?, bureau=?, job_title=?,
                mpl_level=?, work_location=?, date_joined=?, years_in_bureau=?,
                years_in_department=?, avg_perf_3yr=?, has_discipline_issue=?,
                technical_skills=?, soft_skills=?, certifications=?, notes=?,
                is_candidate_bureau_head=?, data_quality_score=?, last_updated=?
            WHERE employee_id=?
        """, (
            row["full_name"], row["email"], row["department"], row["bureau"],
            row["job_title"], row["mpl_level"], row["work_location"], row["date_joined"],
            row["years_in_bureau"], row["years_in_department"], row["avg_perf_3yr"],
            row["has_discipline_issue"], row["technical_skills"], row["soft_skills"],
            row["certifications"], row["notes"], row["is_candidate_bureau_head"],
            row["data_quality_score"], row["last_updated"], row["employee_id"]
        ))

        conn.commit()

        audit_engine.log_update(user_role, emp_id, before, after)

        st.success("✅ Data berhasil **DIPERBARUI**.")
        return

    # ============================
    # INSERT MODE
    # ============================
    cur.execute("""
        INSERT INTO employees (
            employee_id, full_name, email, department, bureau, job_title,
            mpl_level, work_location, date_joined, years_in_bureau,
            years_in_department, avg_perf_3yr, has_discipline_issue,
            technical_skills, soft_skills, certifications, notes,
            is_candidate_bureau_head, data_quality_score, last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["employee_id"], row["full_name"], row["email"],
        row["department"], row["bureau"], row["job_title"],
        row["mpl_level"], row["work_location"], row["date_joined"],
        row["years_in_bureau"], row["years_in_department"],
        row["avg_perf_3yr"], row["has_discipline_issue"],
        row["technical_skills"], row["soft_skills"], row["certifications"],
        row["notes"], row["is_candidate_bureau_head"],
        row["data_quality_score"], row["last_updated"]
    ))

    conn.commit()
    audit_engine.log_insert(user_role, emp_id, row)

    st.success("🎉 Data pegawai baru berhasil ditambahkan.")
