import streamlit as st
import pandas as pd
import json
import ast
from db import get_conn


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


def build_diffs(before, after):
    fields = sorted(set(before.keys()) | set(after.keys()))
    diffs = []
    for f in fields:
        b = before.get(f)
        a = after.get(f)
        if b != a:
            diffs.append({"field": f, "before": b, "after": a})
    return diffs


def render_insert(after):
    st.write("### Data Baru")
    for k, v in after.items():
        st.write(f"**{k}**: {v}")


def render_diff(before, after):
    diffs = build_diffs(before, after)

    if not diffs:
        st.info("Tidak ada perubahan field.")
        return

    st.write("### 🔄 Perubahan Field:")
    for d in diffs:
        st.write(f"**{d['field']}**")
        st.write(f"- Before: `{d['before']}`")
        st.write(f"- After: `{d['after']}`")
        st.write("---")


def render_audit():
    st.subheader("🕒 Audit Trail")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada log.")
        return

    df["date"] = df["action_time"].str[:10]

    for date, group in df.groupby("date"):
        st.markdown(f"## 📅 {date}")

        for _, row in group.iterrows():
            st.write(f"### 🔧 {row['action_type']} | 🆔 {row['employee_id']} 🚹 {row['user_role']}")

            with st.expander("Detail Perubahan"):
                before = safe_json(row["before_data"])
                after = safe_json(row["after_data"])

                if row["action_type"] == "INSERT":
                    render_insert(after)
                else:
                    render_diff(before, after)
