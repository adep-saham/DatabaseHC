import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import plotly.graph_objects as go
from db import get_conn
import io

# ==========================================================
# SAFE VALUE HANDLERS
# ==========================================================
def safe_int(x):
    try:
        if x is None or x == "":
            return 0
        return int(float(x))
    except:
        return 0


def safe_float(x):
    try:
        if x is None or x == "":
            return 0.0
        return float(x)
    except:
        return 0.0


# ==========================================================
# SKILL MATCH (%)
# ==========================================================
def compute_skill_match(candidate_skills, required_skills):
    if not candidate_skills:
        return 0.0

    cand = set([s.strip().lower() for s in str(candidate_skills).split(",") if s.strip()])
    req = set([s.strip().lower() for s in required_skills if s.strip()])

    if len(req) == 0:
        return 100.0

    match = len(cand & req) / len(req)
    return round(match * 100, 1)


# ==========================================================
# TRI Calculation
# ==========================================================
def compute_TRI(row):
    years = safe_int(row.get("years_in_department"))
    perf = safe_float(row.get("avg_perf_3yr"))
    discipline = safe_int(row.get("has_discipline_issue"))

    score = years * 2 + perf * 10
    if discipline:
        score -= 15

    return max(0, min(100, score))


# ==========================================================
# RADAR CHART MINI (FIGSIZE SMALL, PROPORTIONAL)
# ==========================================================

def plot_radar_chart(values, labels, title):

    N = len(values)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    values = values + values[:1]
    angles = angles + angles[:1]

    # Figure mini
    fig, ax = plt.subplots(figsize=(2, 2), dpi=80, subplot_kw=dict(polar=True))
    ax.set_aspect("equal")

    ax.plot(angles, values, linewidth=1.3)
    ax.fill(angles, values, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=7)

    ax.set_yticklabels([])
    ax.set_title(title, fontsize=9, pad=10)

    plt.tight_layout(pad=0.1)

    # ------------------------------
    #  RENDER PNG MINI AGAR TIDAK DI-RESCALE STREAMLIT
    # ------------------------------
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    st.image(buf, width=220)   # << INI MENGUNCI UKURAN




# ==========================================================
# MAIN SCREENING
# ==========================================================
def render_screening():

    st.subheader("📊 Screening Kandidat & Talent Readiness (Level 2)")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()

    if df.empty:
        st.warning("Belum ada data pegawai.")
        return

    # Columns required
    required_cols = [
        "department", "bureau", "job_title", "years_in_department",
        "avg_perf_3yr", "technical_skills", "soft_skills",
        "certifications", "has_discipline_issue"
    ]

    for c in required_cols:
        if c not in df.columns:
            df[c] = None

    # Compute TRI
    df["TRI"] = df.apply(compute_TRI, axis=1)
    df = df.sort_values("TRI", ascending=False).reset_index(drop=True)

    # Filters
    col1, col2 = st.columns(2)

    dept = col1.selectbox(
        "Filter Department",
        ["Semua"] + sorted(df["department"].dropna().unique().tolist())
    )

    min_tri = col2.slider("Minimal TRI", 0, 100, 0)

    df_filtered = df.copy()
    if dept != "Semua":
        df_filtered = df_filtered[df_filtered["department"] == dept]
    df_filtered = df_filtered[df_filtered["TRI"] >= min_tri]

    # Table
    st.markdown("### 📋 Daftar Kandidat (urut berdasarkan TRI)")

    st.dataframe(
        df_filtered[
            ["employee_id","full_name","department","bureau","job_title",
             "years_in_department","avg_perf_3yr","TRI"]
        ],
        use_container_width=True
    )

    if df_filtered.empty:
        st.info("Tidak ada kandidat pada filter ini.")
        return

    # Select candidate
    st.markdown("### 🔍 Detail Kandidat")

    selected_emp = st.selectbox(
        "Pilih kandidat untuk dianalisis:",
        df_filtered["employee_id"].tolist()
    )

    cand = df_filtered[df_filtered["employee_id"] == selected_emp].iloc[0]

    # Profile card
    st.markdown(
        f"""
        ## 🧑‍💼 {cand['full_name']} ({cand['employee_id']})
        **Jabatan:** {cand['job_title']}  
        **Department:** {cand['department']} | **Bureau:** {cand['bureau']}  
        **MPL Level:** {cand['mpl_level'] or '-'}  
        **TRI Score:** **{cand['TRI']}**
        """
    )

    # Required skills baseline
    required_tech = ["sap", "sql", "python"]
    required_soft = ["leadership", "communication", "coordination"]

    # Radar labels
    labels = ["Experience", "Performance", "Tech Skills", "Soft Skills", "Certifications", "Discipline"]

    # Radar values
    exp_score = min(safe_int(cand["years_in_department"]), 20) * 5
    perf_score = safe_float(cand["avg_perf_3yr"]) * 20
    tech_score = compute_skill_match(cand["technical_skills"], required_tech)
    soft_score = compute_skill_match(cand["soft_skills"], required_soft)

    certs = cand["certifications"] or ""
    cert_count = len([c for c in certs.split(",") if c.strip()])
    cert_score = min(cert_count * 33, 100)

    discipline_score = 0 if safe_int(cand["has_discipline_issue"]) else 100

    radar_values = [
        exp_score,
        perf_score,
        tech_score,
        soft_score,
        cert_score,
        discipline_score
    ]

    # Radar Chart
    st.markdown("### 📊 Radar Kompetensi")
    plot_radar_chart(radar_values, labels, f"Talent Profile – {cand['employee_id']}")

    # Insight summary
    st.markdown("### 💡 Insight Singkat")

    colA, colB = st.columns(2)

    with colA:
        st.write(f"- Pengalaman: **{safe_int(cand['years_in_department'])} tahun**")
        st.write(f"- Kinerja: **{safe_float(cand['avg_perf_3yr']):.2f} / 5**")
        st.write(f"- Disiplin: {'❌ Ada catatan' if safe_int(cand['has_discipline_issue']) else '✔ Bersih'}")

    with colB:
        st.write(f"- Hard Skill Match: **{tech_score}%**")
        st.write(f"- Soft Skill Match: **{soft_score}%**")
        st.write(f"- Sertifikasi: **{cand['certifications'] or 'Tidak ada'}**")

    # Best candidate highlight
    best = df_filtered.iloc[0]
    st.success(
        f"🌟 Kandidat terbaik (berdasarkan filter): **{best['full_name']} ({best['employee_id']})** "
        f"dengan TRI: **{best['TRI']}**."
    )


