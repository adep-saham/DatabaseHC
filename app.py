# =========================================================
# HC SYSTEM & DATA MANAGEMENT - EMPLOYEE DATABASE
# STREAMLIT FULL VERSION (UPDATED BUREAU → DIVISI LABELS)
# =========================================================

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# ---------------------------------------------------------
# CONFIG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="HC System & Data Management - Employee DB",
    layout="wide"
)

st.title("📋 HC Employee Database – HC System & Data Management")

st.caption(
    "Prototype HCIS: database pegawai, validasi otomatis, audit trail, screening kandidat, "
    "dan data governance untuk Bureau Head HC System & Data Management."
)

# ---------------------------------------------------------
# DATABASE HANDLER
# ---------------------------------------------------------
@st.cache_resource
def get_conn():
    return sqlite3.connect("hc_employee.db", check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # MAIN EMPLOYEE TABLE
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT,
            bureau TEXT,
            division TEXT,
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
        """
    )

    # AUDIT LOG TABLE
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


def log_audit(role, action, empid, detail):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_log (action_time, user_role, action_type, employee_id, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (datetime.now().isoformat(timespec="seconds"), role, action, empid, detail)
    )
    conn.commit()


def calculate_data_quality(row: dict) -> float:
    score = 0
    if row.get("employee_id") and row.get("full_name"):
        score += 20
    if row.get("job_title") and row.get("bureau") and row.get("division"):
        score += 20
    if row.get("mpl_level") and row.get("work_location"):
        score += 20
    if row.get("date_joined") and row.get("avg_perf_3yr") is not None:
        score += 20
    if row.get("technical_skills") or row.get("soft_skills") or row.get("certifications"):
        score += 20
    return float(score)


def is_candidate_bureau_head(row: dict) -> bool:
    mpl = (row.get("mpl_level") or "").upper().replace(" ", "")
    mpl_ok = mpl.startswith("M2") or mpl.startswith("M1")

    perf_ok = (row.get("avg_perf_3yr") or 0) >= 3.5
    no_discipline = not row.get("has_discipline_issue", False)

    years_bureau = row.get("years_in_bureau") or 0
    years_dept = row.get("years_in_department") or 0
    tenure_ok = (years_bureau >= 1) or (years_dept >= 4)

    return bool(mpl_ok and perf_ok and no_discipline and tenure_ok)


# ---------------------------------------------------------
# INIT DB
# ---------------------------------------------------------
init_db()

# ---------------------------------------------------------
# SIDEBAR ROLE & NAVIGATION
# ---------------------------------------------------------
st.sidebar.header("🔐 Role & Navigasi")

user_role = st.sidebar.selectbox(
    "Role saat ini:",
    ["Viewer", "HR Admin", "HC System Bureau Head"],
    index=1
)

page = st.sidebar.radio(
    "Pilih Menu",
    [
        "Input / Update Data Pegawai",
        "Daftar Pegawai & Screening Kandidat",
        "Audit Trail",
        "Data Quality Dashboard"
    ]
)


def can_edit():
    if user_role not in ["HR Admin", "HC System Bureau Head"]:
        st.error("Anda tidak memiliki hak edit data (Viewer).")
        return False
    return True


# ---------------------------------------------------------
# PAGE 1: INPUT DATA
# ---------------------------------------------------------
if page == "Input / Update Data Pegawai":
    st.subheader("🧾 Input / Update Data Pegawai")

    with st.form("employee_form"):
        col1, col2 = st.columns(2)

        with col1:
            employee_id = st.text_input("Employee ID *")
            full_name = st.text_input("Nama Lengkap *")
            email = st.text_input("Email (opsional)")
            bureau = st.text_input("Bureau")
            division = st.text_input("Divisi")
            job_title = st.text_input("Jabatan Saat Ini")
            mpl_level = st.text_input("MPL Level (contoh: M25, M19)")
            work_location = st.text_input("Lokasi Kerja")

        with col2:
            date_joined = st.date_input(
                "Tanggal Masuk",
                min_value=date(1980, 1, 1),
                max_value=date.today()
            )
            years_in_bureau = st.number_input(
                "Lama di Bureau (tahun)", min_value=0.0, max_value=50.0, step=0.5
            )
            years_in_department = st.number_input(
                "Lama di Divisi (tahun)", min_value=0.0, max_value=50.0, step=0.5
            )
            avg_perf_3yr = st.number_input(
                "Rata-rata Kinerja 3 Tahun", min_value=0.0, max_value=5.0, step=0.1
            )
            has_discipline_issue = st.checkbox("Ada catatan disiplin?", value=False)

        st.markdown("### Kompetensi & Sertifikasi")
        technical_skills = st.text_area("Technical Skills")
        soft_skills = st.text_area("Soft Skills")
        certifications = st.text_area("Sertifikasi")
        notes = st.text_area("Catatan Tambahan")

        submit = st.form_submit_button("💾 Simpan Data")

    if submit:
        if not can_edit():
            st.stop()

        if not employee_id or not full_name:
            st.error("Employee ID dan Nama wajib diisi.")
            st.stop()

        row = {
            "employee_id": employee_id,
            "full_name": full_name,
            "email": email,
            "bureau": bureau,
            "division": division,
            "job_title": job_title,
            "mpl_level": mpl_level,
            "work_location": work_location,
            "date_joined": date_joined.isoformat(),
            "years_in_bureau": years_in_bureau,
            "years_in_department": years_in_department,
            "avg_perf_3yr": avg_perf_3yr,
            "has_discipline_issue": 1 if has_discipline_issue else 0,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "certifications": certifications,
            "notes": notes
        }

        # Quality score
        dq_score = calculate_data_quality(row)
        candidate = is_candidate_bureau_head(row)

        row["data_quality_score"] = dq_score
        row["is_candidate_bureau_head"] = 1 if candidate else 0
        row["last_updated"] = datetime.now().isoformat(timespec="seconds")

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT id FROM employees WHERE employee_id = ?", (employee_id,))
        exists = cur.fetchone()

        if exists:
            cur.execute(
                """
                UPDATE employees SET
                    full_name=?, email=?, bureau=?, division=?, job_title=?,
                    mpl_level=?, work_location=?, date_joined=?, years_in_bureau=?,
                    years_in_department=?, avg_perf_3yr=?, has_discipline_issue=?,
                    technical_skills=?, soft_skills=?, certifications=?, notes=?,
                    is_candidate_bureau_head=?, data_quality_score=?, last_updated=?
                WHERE employee_id=?
                """,
                (
                    row["full_name"], row["email"], row["bureau"], row["division"],
                    row["job_title"], row["mpl_level"], row["work_location"],
                    row["date_joined"], row["years_in_bureau"], row["years_in_department"],
                    row["avg_perf_3yr"], row["has_discipline_issue"],
                    row["technical_skills"], row["soft_skills"], row["certifications"],
                    row["notes"], row["is_candidate_bureau_head"],
                    row["data_quality_score"], row["last_updated"], row["employee_id"]
                )
            )
            conn.commit()
            log_audit(user_role, "UPDATE", employee_id, "Update data pegawai")
            st.success("Data berhasil diperbarui.")
        else:
            cur.execute(
                """
                INSERT INTO employees (
                    employee_id, full_name, email, bureau, division, job_title,
                    mpl_level, work_location, date_joined, years_in_bureau,
                    years_in_department, avg_perf_3yr, has_discipline_issue,
                    technical_skills, soft_skills, certifications, notes,
                    is_candidate_bureau_head, data_quality_score, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(row.values())
            )
            conn.commit()
            log_audit(user_role, "INSERT", employee_id, "Tambah data pegawai")
            st.success("Data pegawai baru berhasil ditambahkan.")

        st.info(f"Skor kualitas data: **{dq_score}/100** | Kandidat BH: **{'YA' if candidate else 'TIDAK'}**")


# ---------------------------------------------------------
# PAGE 2: DAFTAR & SCREENING
# ---------------------------------------------------------
elif page == "Daftar Pegawai & Screening Kandidat":
    st.subheader("👥 Daftar Pegawai & Screening Bureau Head")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)

    if df.empty:
        st.warning("Belum ada data pegawai.")
    else:
        colA, colB, colC = st.columns(3)

        with colA:
            bureau_filter = st.selectbox(
                "Filter Bureau",
                ["(Semua)"] + sorted(df["bureau"].dropna().unique().tolist())
            )
        with colB:
            division_filter = st.selectbox(
                "Filter Divisi",
                ["(Semua)"] + sorted(df["division"].dropna().unique().tolist())
            )
        with colC:
            only_candidate = st.checkbox("Tampilkan hanya kandidat Bureau Head")

        df_view = df.copy()
        if bureau_filter != "(Semua)":
            df_view = df_view[df_view["bureau"] == bureau_filter]
        if division_filter != "(Semua)":
            df_view = df_view[df_view["division"] == division_filter]
        if only_candidate:
            df_view = df_view[df_view["is_candidate_bureau_head"] == 1]

        st.dataframe(
            df_view[
                [
                    "employee_id", "full_name", "bureau", "division", "job_title",
                    "mpl_level", "avg_perf_3yr", "years_in_bureau",
                    "years_in_department", "is_candidate_bureau_head",
                    "data_quality_score", "last_updated"
                ]
            ].rename(
                columns={
                    "employee_id": "EmpID",
                    "full_name": "Nama",
                    "mpl_level": "MPL",
                    "avg_perf_3yr": "Rata2 Kinerja",
                    "years_in_bureau": "Thn Bureau",
                    "years_in_department": "Thn Divisi",
                    "is_candidate_bureau_head": "Kandidat",
                    "data_quality_score": "Skor Data"
                }
            ),
            use_container_width=True
        )


# ---------------------------------------------------------
# PAGE 3: AUDIT TRAIL
# ---------------------------------------------------------
elif page == "Audit Trail":
    st.subheader("🕒 Audit Trail")

    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT action_time, user_role, action_type, employee_id, detail FROM audit_log ORDER BY action_time DESC",
        conn
    )

    if df.empty:
        st.info("Belum ada aktivitas audit.")
    else:
        st.dataframe(df, use_container_width=True)


# ---------------------------------------------------------
# PAGE 4: DATA QUALITY DASHBOARD
# ---------------------------------------------------------
elif page == "Data Quality Dashboard":
    st.subheader("📊 Data Quality Dashboard")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)

    if df.empty:
        st.warning("Belum ada data.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rata-rata Skor Data", f"{df['data_quality_score'].mean():.1f}/100")
        with col2:
            st.metric("Data Bagus (≥80)", (df['data_quality_score'] >= 80).sum())
        with col3:
            st.metric("Perlu Perbaikan (<60)", (df['data_quality_score'] < 60).sum())

        st.bar_chart(df.set_index("employee_id")["data_quality_score"])

        st.dataframe(
            df[
                ["employee_id", "full_name", "bureau", "division", "job_title",
                 "mpl_level", "data_quality_score", "last_updated"]
            ].rename(
                columns={
                    "employee_id": "EmpID",
                    "full_name": "Nama",
                    "mpl_level": "MPL",
                    "data_quality_score": "Skor Data"
                }
            ),
            use_container_width=True
        )
