import streamlit as st
import pandas as pd
from db import get_conn
from data_strategist import compute_competency_gap, generate_insights


def compute_TRI(row):
    score = 0

    # Experience
    score += min(row["years_in_department"], 20) * 2

    # Performance
    score += row["avg_perf_3yr"] * 10

    # Certifications
    cert_count = len(row["certifications"].split(",")) if row["certifications"] else 0
    score += cert_count * 5

    # Discipline penalty
    if row["has_discipline_issue"]:
        score -= 15

    # Normalize
    return max(0, min(100, score))


def render_screening():

    st.subheader("📊 Screening Kandidat & Talent Readiness")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()

    if df.empty:
        st.warning("Belum ada data pegawai.")
        return

    # Compute TRI
    df["TRI"] = df.apply(compute_TRI, axis=1)
    df = df.sort_values("TRI", ascending=False)

    # Filters
    dept = st.selectbox("Filter Department", ["Semua"] + sorted(df["department"].unique()))
    if dept != "Semua":
        df = df[df["department"] == dept]

    min_tri = st.slider("Filter minimal TRI", 0, 100, 0)
    df = df[df["TRI"] >= min_tri]

    st.dataframe(df[
        ["employee_id", "full_name", "department", "bureau", 
         "job_title", "mpl_level", "avg_perf_3yr", 
         "years_in_department", "TRI"]
    ], use_container_width=True)

    # Best candidate highlight
    if len(df) > 0:
        best = df.iloc[0]
        st.success(
            f"🌟 Kandidat terkuat: **{best['full_name']}** "
            f"(TRI: {best['TRI']})"
        )
