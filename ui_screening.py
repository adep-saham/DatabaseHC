import streamlit as st
import pandas as pd
from db import get_conn
from data_strategist import run_data_strategist_pipeline

REQUIRED = {
    "technical": ["hcis", "data", "sql", "sap", "etl", "data governance"],
    "soft": ["analytical", "communication", "coordination", "leadership"]
}

def render_screening():
    st.subheader("👥 Screening Kandidat Bureau Head")

    df = pd.read_sql_query("SELECT * FROM employees", get_conn())
    if df.empty:
        st.warning("Belum ada data.")
        return

    dfp, insights = run_data_strategist_pipeline(df, REQUIRED)

    dept = st.selectbox("Department", ["(Semua)"] + sorted(dfp["department"].unique()))
    bureau = st.selectbox("Bureau", ["(Semua)"] + sorted(dfp["bureau"].unique()))
    only_bh = st.checkbox("Hanya kandidat BH")

    view = dfp.copy()
    if dept != "(Semua)": view = view[view["department"] == dept]
    if bureau != "(Semua)": view = view[view["bureau"] == bureau]
    if only_bh: view = view[view["is_candidate_bureau_head"] == 1]

    st.dataframe(view)

    st.write("### Strategic Insights")
    for i in insights:
        st.write("•", i)
