import streamlit as st
import pandas as pd
import json
import ast
from db import get_conn
from utils import diff_changes


# =========================================================
# SAFE PARSER – Menerima JSON atau dict Python string
# =========================================================
def safe_json_loads(raw):
    """
    Decode string dengan fallback:
    1) JSON valid → json.loads()
    2) Dict Python → ast.literal_eval()
    3) Jika gagal → return {}
    """
    if raw is None or raw == "":
        return {}

    # Coba JSON normal
    try:
        return json.loads(raw)
    except:
        pass

    # Coba Python dict string
    try:
        return ast.literal_eval(raw)
    except:
        return {}


# =========================================================
# BEAUTIFUL DIFF TABLE
# =========================================================
def render_diff_table(before, after):
    diffs = diff_changes(before, after)

    if not diffs:
        st.info("Tidak ada perubahan field.")
        return

    st.markdown("""
    <table style="width:100%; border-collapse:collapse; margin-top:10px;">
        <tr style="background:#F2F2F2; border-bottom:2px solid #CCC;">
            <th style="padding:8px; text-align:left;">Field</th>
            <th style="padding:8px; text-align:left;">Before</th>
            <th style="padding:8px; text-align:left;">After</th>
        </tr>
    """, unsafe_allow_html=True)

    for d in diffs:
        st.markdown(f"""
        <tr>
            <td style="padding:8px; border-top:1px solid #DDD;">
                <b>{d['field']}</b>
            </td>
            <td style="padding:8px; border-top:1px solid #DDD; color:#B00020;">
                {d['before']}
            </td>
            <td style="padding:8px; border-top:1px solid #DDD; color:#006400; font-weight:bold;">
                {d['after']}
            </td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</table>", unsafe_allow_html=True)


# =========================================================
# MAIN AUDIT VIEW (FINAL VERSION)
# =========================================================
def render_audit():
    st.subheader("🕒 Audit Trail (Simple & Powerful)")

    # Ambil data
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM audit_log ORDER BY action_time DESC",
        conn
    )

    if df.empty:
        st.info("Belum ada log.")
        return

    # Group berdasarkan tanggal
    df["date_only"] = df["action_time"].str[:10]

    for date, group in df.groupby("date_only"):
        st.markdown(f"## 📅 {date}")

        for _, row in group.iterrows():

            log_type = row["action_type"]
            emp_id = row["employee_id"]
            time = row["action_time"]
            user = row["user_role"]

            # ============= CARD HEADER =============
            st.markdown(f"""
            <div style="
                padding:14px;
                border-radius:8px;
                border:1px solid #DDD;
                background:#FAFAFA;
                margin-bottom:6px;">
                <b>🔧 {log_type}</b> &nbsp; | &nbsp; <b>🆔 {emp_id}</b><br>
                👤 {user} &nbsp; • &nbsp; 🕒 {time}
            </div>
            """, unsafe_allow_html=True)

            # ============= DETAILS =============
            with st.expander("Detail Perubahan"):

                before_raw = row.get("before_data", "")
                after_raw = row.get("after_data", "")

                before = safe_json_loads(before_raw)
                after = safe_json_loads(after_raw)

                # Jika log lama (INSERT) → hanya tampil detail
                if log_type == "INSERT":
                    st.info("INSERT: Tidak ada before data.")
                    st.json(after)
                    continue

                # Jika UPDATE tetapi tidak ada before/after → tampilkan raw detail
                if before == {} and after == {}:
                    st.warning("Detail tidak dapat diproses, menampilkan raw data:")
                    st.code(row.get("detail", ""), language="json")
                    continue

                # Tampilkan tabel diff
                render_diff_table(before, after)
