import streamlit as st
import pandas as pd
import json
import ast
from db import get_conn
from utils import diff_changes


def safe_json(raw):
    if raw in [None, "", "null"]:
        return {}
    try:
        return json.loads(raw)
    except:
        try:
            return ast.literal_eval(raw)
        except:
            return {}


def render_diff(before, after):
    diffs = diff_changes(before, after)

    if not diffs:
        st.info("Tidak ada perubahan field.")
        return

    st.write("### 🔄 Perubahan Field")

    st.markdown("""
    <table style='width:100%;border-collapse:collapse;margin-top:10px;'>
        <tr style='background:#EEE;font-weight:bold;'>
            <td style='padding:8px;border:1px solid #DDD;'>Field</td>
            <td style='padding:8px;border:1px solid #DDD;'>Before</td>
            <td style='padding:8px;border:1px solid #DDD;'>After</td>
        </tr>
    """, unsafe_allow_html=True)

    for d in diffs:
        st.markdown(f"""
        <tr>
            <td style='padding:8px;border:1px solid #DDD;'>{d['field']}</td>
            <td style='padding:8px;border:1px solid #DDD;color:#B00020;'>{d['before']}</td>
            <td style='padding:8px;border:1px solid #DDD;color:#006400;font-weight:bold;'>{d['after']}</td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</table>", unsafe_allow_html=True)


def render_audit():
    st.subheader("🕒 Audit Trail (Simple & Powerful)")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)

    if df.empty:
        st.info("Belum ada log.")
        return

    df["date"] = df["action_time"].str[:10]

    for date, group in df.groupby("date"):
        st.markdown(f"## 📅 {date}")

        for _, row in group.iterrows():

            st.markdown(f"""
            <div style='padding:12px;border:1px solid #DDD;background:#FAFAFA;margin-bottom:6px;'>
                <b>🔧 {row['action_type']}</b> | 🆔 {row['employee_id']}<br>
                👤 {row['user_role']} • 🕒 {row['action_time']}
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Detail Perubahan"):
                before = safe_json(row["before_data"])
                after = safe_json(row["after_data"])

                if row["action_type"] == "INSERT":
                    st.info("INSERT: Menampilkan data baru.")
                    st.json(after)
                    continue

                if before == {} and after == {}:
                    st.warning("Data before/after kosong. Menampilkan detail mentah:")
                    st.code(row["detail"])
                    continue

                render_diff(before, after)
