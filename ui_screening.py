import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

from db import get_conn


# ============================================
# Helper untuk angka aman
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
# Skill Match (%)
# ============================================
def compute_skill_match(candidate_skills, required_skills):
    if not candidate_skills:
        return 0.0

    cand = set([s.strip().lower() for s in str(candidate_skills).split(",") if s.strip()])
    req = set([s.strip().lower() for s in required_skills if s.strip()])

    if len(req) == 0:
        return 100.0

    match = len(cand & req) / len(req)
    return round(match * 100, 1)


# ============================================
# Talent Readiness Index (TRI) sederhana
# ============================================
def compute_TRI(row):
    years = safe_int(row.get("years_in_department"))
    perf = safe_float(row.get("avg_perf_3yr"))
    has_issue = safe_int(row.get("has_discipline_issue"))

    score = 0
    score += min(years, 20) * 2          # 0–40
    score += perf * 10                   # 0–50
    if has_issue:
        score -= 15                      # penalti

    return max(0, min(100, score))


# ============================================
# Radar chart plotting
# ============================================
def plot_radar_chart(values, labels, title):
    N = len(values)

    angles = [n / float(N) * 2 * pi for n in range(N)]
    values = values + values[:1]
    angles = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(3,3), subplot_kw=dict(polar=True))
    ax.set_aspect('equal')

    ax.plot(angles, values, linewidth=2, linestyle='solid')
    ax.fill(angles, values, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)

    ax.set_yticklabels([])
    ax.set_title(title, fontsize=10, pad=10)

    plt.tight_layout(pad=0.4)
    st.pyplot(fig)



# ============================================
# Hitung skor untuk radar chart
# ============================================
def compute_radar_scores(row, required_tech, required_soft):
    years = safe_int(row.get("years_in_department"))
    perf = safe_float(row.get("avg_perf_3yr"))
    has_issue = safe_int(row.get("has_discipline_issue"))
    tech = row.get("technical_skills", "")
    soft = row.get("soft_skills", "")
    certs = row.get("certifications", "")

    exp_score = min(years, 20) * 5            # max 100
    perf_score = max(0.0, min(100.0, perf * 20))  # 5.0 -> 100
    tech_score = compute_skill_match(tech, required_tech)
    soft_score = compute_skill_match(soft, required_soft)

    cert_count = len([c for c in str(certs).split(",") if c.strip()]) if certs else 0
    cert_score = min(cert_count * 33, 100)    # 0,33,66,99,...

    discipline_score = 0 if has_issue else 100

    return [exp_score, perf_score, tech_score, soft_score, cert_score, discipline_score]


# ============================================
# MAIN SCREENING FUNCTION (dipanggil dari app.py)
# ============================================
def render_screening():

    st.subheader("📊 Screening Kandidat & Talent Readiness (Level 2)")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()

    if df.empty:
        st.warning("Belum ada data pegawai.")
        return

    # Pastikan kolom penting ada
    required_cols = [
        "department", "bureau", "job_title", "years_in_department",
        "avg_perf_3yr", "technical_skills", "soft_skills",
        "certifications", "has_discipline_issue"
    ]
    for c in required_cols:
        if c not in df.columns:
            df[c] = None

    # Hitung TRI
    df["TRI"] = df.apply(compute_TRI, axis=1)
    df = df.sort_values("TRI", ascending=False).reset_index(drop=True)

    # =========================
    # FILTER GLOBAL
    # =========================
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        dept_filter = st.selectbox(
            "Filter Department",
            ["Semua"] + sorted(df["department"].dropna().unique().tolist())
        )

    with col_f2:
        min_tri = st.slider("Filter minimal TRI", 0, 100, 0)

    df_filtered = df.copy()
    if dept_filter != "Semua":
        df_filtered = df_filtered[df_filtered["department"] == dept_filter]
    df_filtered = df_filtered[df_filtered["TRI"] >= min_tri]

    # =========================
    # TABEL KANDIDAT
    # =========================
    st.markdown("### 📄 Daftar Kandidat (urut TRI)")

    st.dataframe(
        df_filtered[
            [
                "employee_id", "full_name", "department", "bureau", "job_title",
                "mpl_level", "years_in_department", "avg_perf_3yr", "TRI"
            ]
        ],
        use_container_width=True
    )

    if df_filtered.empty:
        st.info("Tidak ada kandidat yang memenuhi filter saat ini.")
        return

    # =========================
    # PILIH SATU KANDIDAT
    # =========================
    st.markdown("### 🔍 Detail Kandidat")

    selected_emp = st.selectbox(
        "Pilih kandidat untuk dianalisis:",
        df_filtered["employee_id"].tolist()
    )

    cand = df_filtered[df_filtered["employee_id"] == selected_emp].iloc[0]

    # =========================
    # PROFILE CARD
    # =========================
    st.markdown(
        f"""
        #### 🧑‍💼 {cand['full_name']} ({cand['employee_id']})
        **Jabatan:** {cand['job_title']}  
        **Department:** {cand['department']} | **Bureau:** {cand['bureau']}  
        **MPL Level:** {cand.get('mpl_level', '') or '-'}  
        **TRI Score:** **{cand['TRI']}**
        """
    )

    # =========================
    # RADAR CHART
    # =========================
    st.markdown("#### 📊 Radar Kompetensi")

    required_tech = ["sap", "sql", "python"]
    required_soft = ["leadership", "communication", "coordination"]

    labels = ["Experience", "Performance", "Tech Skills", "Soft Skills", "Certifications", "Discipline"]
    radar_values = compute_radar_scores(cand, required_tech, required_soft)

    plot_radar_chart(radar_values, labels, f"Talent Profile – {cand['employee_id']}")

    # =========================
    # RINGKASAN ANGKA
    # =========================
    st.markdown("#### 💡 Insight Singkat")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"- Pengalaman di departemen: **{safe_int(cand['years_in_department'])} tahun**")
        st.write(f"- Rata-rata kinerja 3 tahun: **{safe_float(cand['avg_perf_3yr']):.2f} / 5**")
        st.write(f"- Disiplin: {'❌ Ada catatan' if safe_int(cand['has_discipline_issue']) else '✔ Bersih'}")

    with col2:
        tech_match = compute_skill_match(cand["technical_skills"], required_tech)
        soft_match = compute_skill_match(cand["soft_skills"], required_soft)

        st.write(f"- Hard Skill Match: **{tech_match}%** (vs {', '.join(required_tech)})")
        st.write(f"- Soft Skill Match: **{soft_match}%** (vs {', '.join(required_soft)})")
        st.write(f"- Sertifikasi: **{cand['certifications'] or 'Tidak ada'}**")

    # Highlight kandidat terkuat di filter
    best = df_filtered.iloc[0]
    st.markdown("---")
    st.success(
        f"🌟 Kandidat terkuat di filter ini: **{best['full_name']} ({best['employee_id']})** "
        f"dengan TRI **{best['TRI']}**."
    )

