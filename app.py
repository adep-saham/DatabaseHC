# app.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import random

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="HC System & Data Management - Employee DB",
    layout="wide"
)

st.title("📋 HC Employee Database – HC System & Data Management")

st.caption(
    "Prototype HCIS: data pegawai, validasi otomatis, audit trail, dan screening kandidat "
    "Bureau Head HC System & Data Management."
)

# =========================================================
# DATABASE HELPER
# =========================================================
@st.cache_resource
def get_conn():
    conn = sqlite3.connect("hc_employee.db", check_same_thread=False)
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Tabel utama pegawai
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            bureau TEXT,
            job_title TEXT,
            mpl_level TEXT,               -- M25-M19 dll
            work_location TEXT,
            date_joined TEXT,
            years_in_bureau REAL,
            years_in_department REAL,
            avg_perf_3yr REAL,
            has_discipline_issue INTEGER,  -- 0/1
            technical_skills TEXT,
            soft_skills TEXT,
            certifications TEXT,
            notes TEXT,
            is_candidate_bureau_head INTEGER, -- 0/1
            data_quality_score REAL,
            last_updated TEXT
        )
        """
    )

    # Tabel audit trail
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_time TEXT,
            user_role TEXT,
            action_type TEXT,
            employee_id TEXT,
            detail TEXT
        )
        """
    )

    conn.commit()


def log_audit(user_role: str, action_type: str, employee_id: str, detail: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_log (action_time, user_role, action_type, employee_id, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (datetime.now().isoformat(timespec="seconds"), user_role, action_type, employee_id, detail),
    )
    conn.commit()


def calculate_data_quality(row: dict) -> float:
    """
    Skor sederhana 0–100:
    +20: employee_id, full_name terisi
    +20: jabatan, department, bureau terisi
    +20: MPL dan lokasi kerja terisi
    +20: tanggal masuk & rata-rata kinerja terisi
    +20: informasi kompetensi (technical/soft/sertifikasi) terisi
    """
    score = 0

    if row.get("employee_id") and row.get("full_name"):
        score += 20
    if row.get("job_title") and row.get("department") and row.get("bureau"):
        score += 20
    if row.get("mpl_level") and row.get("work_location"):
        score += 20
    if row.get("date_joined") and row.get("avg_perf_3yr") is not None:
        score += 20
    if row.get("technical_skills") or row.get("soft_skills") or row.get("certifications"):
        score += 20

    return float(score)


def is_candidate_bureau_head(row: dict) -> bool:
    """
    Rule sederhana berdasarkan flyer:
    - MPL antara M25–M19
    - Avg performance 3 tahun >= 3.5 (bisa sesuaikan)
    - Tidak ada catatan disiplin
    - Lama di Bureau >= 1 tahun ATAU lama di Department >= 4 tahun
    """
    mpl = (row.get("mpl_level") or "").upper().replace(" ", "")
    mpl_ok = mpl.startswith("M2") or mpl.startswith("M1")  # simple check

    perf = row.get("avg_perf_3yr") or 0
    perf_ok = perf >= 3.5

    no_discipline = not row.get("has_discipline_issue", False)

    years_bureau = row.get("years_in_bureau") or 0
    years_dept = row.get("years_in_department") or 0
    tenure_ok = (years_bureau >= 1) or (years_dept >= 4)

    return bool(mpl_ok and perf_ok and no_discipline and tenure_ok)


# =========================================================
# SIDEBAR – ROLE & NAVIGATION
# =========================================================
init_db()

st.sidebar.header("🔐 User & Navigasi")

user_role = st.sidebar.selectbox(
    "Peran saat ini (simulasi RBAC)",
    ["Viewer", "HR Admin", "HC System Bureau Head"],
    index=1
)

page = st.sidebar.radio(
    "Pilih menu",
    [
        "Input / Update Data Pegawai",
        "Generate Dummy Data (100)",
        "Daftar Pegawai & Screening Kandidat",
        "Audit Trail",
        "Data Quality Dashboard",
    ]
)

st.sidebar.info(
    "Peran **HR Admin / HC System Bureau Head** dapat menambah & mengubah data. "
    "Peran **Viewer** hanya dapat melihat."
)


def check_edit_permission():
    if user_role not in ["HR Admin", "HC System Bureau Head"]:
        st.error("Anda tidak memiliki hak untuk mengubah data (role Viewer).")
        return False
    return True


# =========================================================
# PAGE 1 – INPUT / UPDATE DATA
# =========================================================
if page == "Input / Update Data Pegawai":
    st.subheader("🧾 Input / Update Data Pegawai")

    st.markdown(
        "Form ini sudah dilengkapi **validasi otomatis** untuk mengurangi risiko human error "
        "dan memastikan kelengkapan data kunci."
    )

    with st.form("employee_form"):
        col1, col2 = st.columns(2)

        with col1:
            employee_id = st.text_input("Employee ID *")
            full_name = st.text_input("Nama Lengkap *")
            email = st.text_input("Email (opsional)")
            department = st.text_input("Department")
            bureau = st.text_input("Bureau / Unit")
            job_title = st.text_input("Jabatan Saat Ini")
            mpl_level = st.text_input("MIND ID Person Level (MPL) – contoh: M25, M22, M19")
            work_location = st.text_input("Lokasi Kerja")

        with col2:
            date_joined = st.date_input(
                "Tanggal Masuk Perusahaan",
                min_value=date(1980, 1, 1),
                max_value=date.today()
            )
            years_in_bureau = st.number_input(
                "Lama bekerja di Bureau (tahun)",
                min_value=0.0,
                max_value=50.0,
                step=0.5
            )
            years_in_department = st.number_input(
                "Lama bekerja di Department (tahun)",
                min_value=0.0,
                max_value=50.0,
                step=0.5
            )
            avg_perf_3yr = st.number_input(
                "Rata-rata Nilai Kinerja 3 Tahun Terakhir",
                min_value=0.0,
                max_value=5.0,
                step=0.1
            )
            has_discipline_issue = st.checkbox("Ada catatan disiplin?", value=False)

        st.markdown("### Kompetensi & Sertifikasi")
        technical_skills = st.text_area(
            "Technical Skills (misal: HCIS, HR Analytics, ETL, SAP/ERP, Data Governance)"
        )
        soft_skills = st.text_area(
            "Soft Skills (misal: komunikasi, koordinasi, analitis, leadership)"
        )
        certifications = st.text_area(
            "Sertifikasi (misal: HC, IT, Data Management, Project Management)"
        )
        notes = st.text_area("Catatan tambahan (opsional)")

        submitted = st.form_submit_button("💾 Simpan / Update")

    if submitted:
        if not check_edit_permission():
            st.stop()

        # --- VALIDASI SEDERHANA ---
        if not employee_id.strip():
            st.error("Employee ID wajib diisi.")
            st.stop()
        if not full_name.strip():
            st.error("Nama lengkap wajib diisi.")
            st.stop()

        if email and "@" not in email:
            st.warning("Format email tampaknya tidak valid, namun tetap akan disimpan.")

        # Build row dict
        row = dict(
            employee_id=employee_id.strip(),
            full_name=full_name.strip(),
            email=email.strip(),
            department=department.strip(),
            bureau=bureau.strip(),
            job_title=job_title.strip(),
            mpl_level=mpl_level.strip(),
            work_location=work_location.strip(),
            date_joined=date_joined.isoformat() if date_joined else "",
            years_in_bureau=float(years_in_bureau),
            years_in_department=float(years_in_department),
            avg_perf_3yr=float(avg_perf_3yr) if avg_perf_3yr else None,
            has_discipline_issue=1 if has_discipline_issue else 0,
            technical_skills=technical_skills.strip(),
            soft_skills=soft_skills.strip(),
            certifications=certifications.strip(),
            notes=notes.strip(),
        )

        dq_score = calculate_data_quality(row)
        row["data_quality_score"] = dq_score
        candidate_flag = is_candidate_bureau_head(row)
        row["is_candidate_bureau_head"] = 1 if candidate_flag else 0
        row["last_updated"] = datetime.now().isoformat(timespec="seconds")

        # Insert / update ke DB
        conn = get_conn()
        cur = conn.cursor()

        # Cek apakah sudah ada
        cur.execute("SELECT id FROM employees WHERE employee_id = ?", (row["employee_id"],))
        existing = cur.fetchone()

        if existing:
            # Update
            cur.execute(
                """
                UPDATE employees
                SET full_name = ?,
                    email = ?,
                    department = ?,
                    bureau = ?,
                    job_title = ?,
                    mpl_level = ?,
                    work_location = ?,
                    date_joined = ?,
                    years_in_bureau = ?,
                    years_in_department = ?,
                    avg_perf_3yr = ?,
                    has_discipline_issue = ?,
                    technical_skills = ?,
                    soft_skills = ?,
                    certifications = ?,
                    notes = ?,
                    is_candidate_bureau_head = ?,
                    data_quality_score = ?,
                    last_updated = ?
                WHERE employee_id = ?
                """,
                (
                    row["full_name"],
                    row["email"],
                    row["department"],
                    row["bureau"],
                    row["job_title"],
                    row["mpl_level"],
                    row["work_location"],
                    row["date_joined"],
                    row["years_in_bureau"],
                    row["years_in_department"],
                    row["avg_perf_3yr"],
                    row["has_discipline_issue"],
                    row["technical_skills"],
                    row["soft_skills"],
                    row["certifications"],
                    row["notes"],
                    row["is_candidate_bureau_head"],
                    row["data_quality_score"],
                    row["last_updated"],
                    row["employee_id"],
                ),
            )
            conn.commit()
            log_audit(user_role, "UPDATE", row["employee_id"], "Update data pegawai")
            st.success(f"Data pegawai dengan ID {row['employee_id']} berhasil diupdate.")
        else:
            # Insert baru
            cur.execute(
                """
                INSERT INTO employees (
                    employee_id, full_name, email, department, bureau, job_title,
                    mpl_level, work_location, date_joined, years_in_bureau,
                    years_in_department, avg_perf_3yr, has_discipline_issue,
                    technical_skills, soft_skills, certifications, notes,
                    is_candidate_bureau_head, data_quality_score, last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["employee_id"],
                    row["full_name"],
                    row["email"],
                    row["department"],
                    row["bureau"],
                    row["job_title"],
                    row["mpl_level"],
                    row["work_location"],
                    row["date_joined"],
                    row["years_in_bureau"],
                    row["years_in_department"],
                    row["avg_perf_3yr"],
                    row["has_discipline_issue"],
                    row["technical_skills"],
                    row["soft_skills"],
                    row["certifications"],
                    row["notes"],
                    row["is_candidate_bureau_head"],
                    row["data_quality_score"],
                    row["last_updated"],
                ),
            )
            conn.commit()
            log_audit(user_role, "INSERT", row["employee_id"], "Input data pegawai baru")
            st.success(f"Data pegawai dengan ID {row['employee_id']} berhasil disimpan.")

        st.info(
            f"Skor kualitas data: **{dq_score:.0f}/100** | "
            f"Kandidat Bureau Head: **{'YA' if candidate_flag else 'TIDAK'}**"
        )


# =========================================================
# PAGE – GENERATE 100 DUMMY DATA
# =========================================================
elif page == "Generate Dummy Data (100)":
    st.subheader("🤖 Generate 100 Dummy Data Pegawai")

    st.warning(
        "Aksi ini akan **menghapus seluruh data pegawai yang ada** kemudian mengisi ulang "
        "dengan 100 data dummy untuk keperluan simulasi."
    )

    if not check_edit_permission():
        st.stop()

    if st.button("🚀 Hapus & Generate 100 Dummy Pegawai"):
        conn = get_conn()
        cur = conn.cursor()

        # Hapus semua data existing
        cur.execute("DELETE FROM employees")
        conn.commit()

        names = ["Ari", "Budi", "Citra", "Dewa", "Elsa", "Fikri", "Gita", "Hana", "Indra", "Joko"]
        lastnames = ["Pratama", "Wibowo", "Santoso", "Saputra", "Wijaya", "Firmansyah", "Putri"]

        depts = ["Corporate Services", "Finance", "Internal Audit", "Operations", "HC System"]
        bureaus = ["IT Governance", "HC Data Management", "Payroll", "Recruitment", "Training"]

        for i in range(1, 101):
            emp_id = f"EMP{i:03d}"
            full = f"{random.choice(names)} {random.choice(lastnames)}"
            dept = random.choice(depts)
            bur = random.choice(bureaus)
            job = random.choice(["Officer", "Analyst", "Senior Analyst", "Supervisor", "Manager"])
            mpl = random.choice(["M25", "M24", "M23", "M22", "M21", "M19"])
            loc = random.choice(["Jakarta", "Bogor", "Bekasi", "Bandung", "Site UBPN"])

            join_date = f"20{random.randint(13, 23)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            years_bureau = round(random.uniform(0, 8), 1)
            years_dept = round(random.uniform(0, 12), 1)
            perf = round(random.uniform(2.0, 5.0), 2)

            disc = random.choice([0, 0, 0, 1])  # 25% chance punya catatan disiplin

            tech = random.choice(["HCIS", "SAP", "Data Governance", "Python", "ETL", "None"])
            soft = random.choice(["Analytical", "Communication", "Leadership", "Coordination"])
            cert = random.choice(["HC Cert", "ITIL", "COBIT", "None"])

            row = {
                "employee_id": emp_id,
                "full_name": full,
                "email": f"{emp_id.lower()}@example.com",
                "department": dept,
                "bureau": bur,
                "job_title": job,
                "mpl_level": mpl,
                "work_location": loc,
                "date_joined": join_date,
                "years_in_bureau": years_bureau,
                "years_in_department": years_dept,
                "avg_perf_3yr": perf,
                "has_discipline_issue": disc,
                "technical_skills": tech,
                "soft_skills": soft,
                "certifications": cert,
                "notes": "",
            }

            dq = calculate_data_quality(row)
            is_bh = 1 if is_candidate_bureau_head(row) else 0
            last = datetime.now().isoformat(timespec="seconds")

            cur.execute(
                """
                INSERT INTO employees (
                    employee_id, full_name, email, department, bureau, job_title,
                    mpl_level, work_location, date_joined, years_in_bureau,
                    years_in_department, avg_perf_3yr, has_discipline_issue,
                    technical_skills, soft_skills, certifications, notes,
                    is_candidate_bureau_head, data_quality_score, last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["employee_id"], row["full_name"], row["email"],
                    row["department"], row["bureau"], row["job_title"],
                    row["mpl_level"], row["work_location"], row["date_joined"],
                    row["years_in_bureau"], row["years_in_department"],
                    row["avg_perf_3yr"], row["has_discipline_issue"],
                    row["technical_skills"], row["soft_skills"], row["certifications"], row["notes"],
                    is_bh, dq, last
                )
            )

            log_audit(user_role, "INSERT_DUMMY", row["employee_id"], "Generate dummy employee")

        conn.commit()
        st.success("🎉 100 dummy data pegawai berhasil dibuat!")
        st.balloons()


# =========================================================
# PAGE 2 – DAFTAR PEGAWAI & SCREENING
# =========================================================
elif page == "Daftar Pegawai & Screening Kandidat":
    st.subheader("👥 Daftar Pegawai & Screening Kandidat Bureau Head")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)

    if df.empty:
        st.warning("Belum ada data pegawai.")
    else:
        # Filter sederhana
        col1, col2, col3 = st.columns(3)
        with col1:
            dept_filter = st.selectbox(
                "Filter Department",
                ["(Semua)"] + sorted(df["department"].dropna().unique().tolist())
            )
        with col2:
            bureau_filter = st.selectbox(
                "Filter Bureau",
                ["(Semua)"] + sorted(df["bureau"].dropna().unique().tolist())
            )
        with col3:
            only_candidate = st.checkbox("Tampilkan hanya kandidat Bureau Head", value=False)

        df_view = df.copy()
        if dept_filter != "(Semua)":
            df_view = df_view[df_view["department"] == dept_filter]
        if bureau_filter != "(Semua)":
            df_view = df_view[df_view["bureau"] == bureau_filter]
        if only_candidate:
            df_view = df_view[df_view["is_candidate_bureau_head"] == 1]

        st.dataframe(
            df_view[
                [
                    "employee_id",
                    "full_name",
                    "department",
                    "bureau",
                    "job_title",
                    "mpl_level",
                    "avg_perf_3yr",
                    "years_in_bureau",
                    "years_in_department",
                    "is_candidate_bureau_head",
                    "data_quality_score",
                    "last_updated",
                ]
            ].rename(
                columns={
                    "employee_id": "EmpID",
                    "full_name": "Nama",
                    "mpl_level": "MPL",
                    "avg_perf_3yr": "Rata2 Kinerja 3th",
                    "years_in_bureau": "Thn di Bureau",
                    "years_in_department": "Thn di Dept",
                    "is_candidate_bureau_head": "Kandidat BH",
                    "data_quality_score": "Skor Data",
                }
            ),
            use_container_width=True,
        )

        st.caption(
            "Kolom **Kandidat BH** = 1 menandakan pegawai memenuhi rule dasar "
            "untuk _HC System & Data Management Bureau Head_ (rotasi/promosi)."
        )


# =========================================================
# PAGE 3 – AUDIT TRAIL
# =========================================================
elif page == "Audit Trail":
    st.subheader("🕒 Audit Trail – Aktivitas Perubahan Data")

    conn = get_conn()
    df_log = pd.read_sql_query(
        "SELECT action_time, user_role, action_type, employee_id, detail FROM audit_log "
        "ORDER BY action_time DESC",
        conn,
    )

    if df_log.empty:
        st.info("Belum ada aktivitas yang terekam.")
    else:
        st.dataframe(df_log, use_container_width=True)
        st.caption(
            "Audit trail mendukung prinsip **akuntabilitas, keamanan, dan kepatuhan** "
            "dalam pengelolaan data HC."
        )


# =========================================================
# PAGE 4 – DATA QUALITY DASHBOARD
# =========================================================
elif page == "Data Quality Dashboard":
    st.subheader("📊 Data Quality Dashboard")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)

    if df.empty:
        st.warning("Belum ada data pegawai.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_score = df["data_quality_score"].mean()
            st.metric("Rata-rata Skor Kualitas Data", f"{avg_score:.1f} / 100")

        with col2:
            cnt_good = (df["data_quality_score"] >= 80).sum()
            st.metric("Data sangat baik (≥80)", cnt_good)

        with col3:
            cnt_bad = (df["data_quality_score"] < 60).sum()
            st.metric("Data perlu perbaikan (<60)", cnt_bad)

        st.markdown("### Distribusi Skor Kualitas Data")
        st.bar_chart(df.set_index("employee_id")["data_quality_score"])

        st.markdown("### Detail Data")
        st.dataframe(
            df[
                [
                    "employee_id",
                    "full_name",
                    "department",
                    "bureau",
                    "job_title",
                    "mpl_level",
                    "data_quality_score",
                    "last_updated",
                ]
            ].rename(
                columns={
                    "employee_id": "EmpID",
                    "full_name": "Nama",
                    "mpl_level": "MPL",
                    "data_quality_score": "Skor Data",
                }
            ),
            use_container_width=True,
        )

        st.caption(
            "Dashboard ini menggambarkan praktik **data quality management** yang sering "
            "muncul di soal: validasi otomatis, pengurangan human error, dan monitoring "
            "kualitas data HC."
        )
