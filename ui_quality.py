import streamlit as st
import pandas as pd
from db import get_conn
from data_strategist import run_data_strategist_pipeline

def render_quality():

    st.subheader("📈 Data Quality Dashboard (Advanced)")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada data.")
        return

    # ==========================================
    # 1. RUN PIPELINE (data_quality + anomaly + gap + TRI)
    # ==========================================
    required_skills = {
        "technical": ["HCIS", "SQL", "SAP"],
        "soft": ["analytical", "communication", "coordination"]
    }

    df_processed, insights = run_data_strategist_pipeline(df, required_skills)

    # ==========================================
    # 2. DISPLAY SUMMARY METRICS
    # ==========================================
    col1, col2, col3 = st.columns(3)

    col1.metric("📉 Rata-rata Data Quality Score", 
                round(df_processed["data_quality_score_adv"].mean(), 1))

    col2.metric("⚠️ Jumlah Anomali", 
                (df_processed["anomaly_flag"] != "OK").sum())

    col3.metric("⭐ Kandidat Siap (TRI ≥ 75)", 
                (df_processed["talent_readiness_index"] >= 75).sum())

    st.markdown("---")

    # ==========================================
    # 3. TABLE DATA QUALITY
    # ==========================================
    st.markdown("### 📊 Tabel Data Kualitas Pegawai")
    st.dataframe(df_processed[
        ["employee_id","full_name",
         "data_quality_score_adv", "anomaly_flag",
         "competency_gap_score","talent_readiness_index"]
    ])

    # ==========================================
    # 4. ANOMALY SECTION
    # ==========================================
    st.markdown("### 🚨 Anomali Data")
    anomaly_df = df_processed[df_processed["anomaly_flag"] != "OK"]

    if anomaly_df.empty:
        st.success("Tidak ada anomali. Data konsisten! 🎉")
    else:
        st.dataframe(anomaly_df[["employee_id","full_name","anomaly_flag"]])

    # ==========================================
    # 5. INSIGHTS
    # ==========================================
    st.markdown("### 💡 HC Insights (Automated)")

    for i in insights:
        st.write(i)
