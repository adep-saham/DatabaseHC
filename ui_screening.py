import streamlit as st
import pandas as pd
from db import get_conn

def render_screening():
    st.subheader("📊 Screening Kandidat & Talent Readiness")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada data.")
        return

    df["Readiness Score"] = (
        df["avg_perf_3yr"].fillna(0)*10
        - df["has_discipline_issue"].fillna(0)*20
        + df["years_in_department"].fillna(0)*2
    )

    st.dataframe(df)
