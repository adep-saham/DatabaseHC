import streamlit as st
import pandas as pd
from db import get_conn

def render_quality():
    st.subheader("📊 Data Quality Dashboard")

    df = pd.read_sql_query("SELECT * FROM employees", get_conn())
    if df.empty:
        st.warning("Belum ada data.")
        return

    st.metric("Rata-rata Skor Data", f"{df['data_quality_score'].mean():.1f}")
    st.dataframe(df)
