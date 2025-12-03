import streamlit as st
import pandas as pd
from db import get_conn

def render_quality():
    st.subheader("📈 Data Quality Dashboard")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada data.")
        return

    df["Missing Fields"] = df.apply(
        lambda r: sum(v in ["", None] for v in r.values),
        axis=1
    )

    st.dataframe(df[["employee_id","full_name","Missing Fields","data_quality_score"]])
