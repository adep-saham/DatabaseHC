import streamlit as st
import pandas as pd
import json
from db import get_conn
from utils import diff_changes

def render_audit():
    st.subheader("🕒 Audit Trail (Simple & Powerful)")

    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM audit_log ORDER BY action_time DESC",
        conn
    )

    if df.empty:
        st.info("Belum ada log.")
        return

    # ===========================
    # GROUP BY DATE
    # ===========================
    df["date_only"] = df["action_time"].str[:10]

    for date, group in df.groupby("date_only"):
        st.markdown(f"## 📅 {date}")

        for _, row in group.iterrows():

            log_type = row["action_type"]
            emp_id = row["employee_id"]
            time = row["action_time"]
            user = row["user_role"]

            # CARD HEADER
            st.markdown(f"""
            <div style="padding:12px; border-radius:8px; border:1px solid #DDD; background:#FAFAFA; margin-bottom:10px;">
                <b>🔧 {log_type}</b> &nbsp; | &nbsp; <b>🆔 {emp_id}</b>  
                <br>👤 {user} &nbsp; • &nbsp; 🕒 {time}
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Detail Perubahan"):

                before_raw = row["before_data"]
                after_raw = row["after_data"]

                try:
                    before = json.loads(before_raw) if before_raw else {}
                    after = json.loads(after_raw) if after_raw else {}
                except:
                    st.warning("Detail tidak dapat diproses.")
                    st.caption(row["detail"])
                    continue

                # Hitung diff memakai utils.diff_changes
                diffs = diff_changes(before, after)

                if not diffs:
                    st.info("Tidak ada perubahan field.")
                    continue

                # Tampilkan diff dalam tabel cantik
                table_md = """
                <table style="width:100%; border-collapse:collapse;">
                    <tr style="background:#EEE;">
                        <th style="padding:6px; border:1px solid #CCC;">Field</th>
                        <th style="padding:6px; border:1px solid #CCC;">Before</th>
                        <th style="padding:6px; border:1px solid #CCC;">After</th>
                    </tr>
                """

                for d in diffs:
                    table_md += f"""
                    <tr>
                        <td style="padding:6px; border:1px solid #CCC; font-weight:bold;">{d['field']}</td>
                        <td style="padding:6px; border:1px solid #CCC; color:#B00020;">{d['before']}</td>
                        <td style="padding:6px; border:1px solid #CCC; color:#006400; font-weight:bold;">{d['after']}</td>
                    </tr>
                    """

                table_md += "</table>"

                st.markdown(table_md, unsafe_allow_html=True)
