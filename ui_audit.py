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
        if before.get(f) != after.get(f):
            diffs.append({"field": f, "before": before.get(f), "after": after.get(f)})
    return diffs

def render_diff(before, after):
    diffs = build_diffs(before, after)
    if not diffs:
        st.info("Tidak ada perubahan field.")
        return

    st.write("### Perubahan Field:")
    for d in diffs:
        st.write(f"**{d['field']}**  \n- Before: `{d['before']}`  \n- After: `{d['after']}`")
        st.write("---")

def render_insert(after):
    st.write("### Data Baru:")
    for k,v in after.items():
        st.write(f"**{k}**: {v}")

def render_audit():
    st.subheader("Audit Trail")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada log.")
        return

    df["date"] = df["action_time"].str[:10]

    # ======= STYLE CSS MINIMALIS =======
    st.markdown("""
    <style>
        .audit-card {
            padding: 10px 15px;
            border-radius: 6px;
            border: 1px solid #DDD;
            margin-bottom: 6px;
            background: #FAFAFA;
        }
        .audit-header {
            font-size: 14px;
            font-weight: 600;
        }
        .audit-meta {
            font-size: 12px;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)
    # ===================================

    for date, group in df.groupby("date"):
        st.markdown(f"### {date}")

        for _, row in group.iterrows():
            st.markdown(
                f"""
                <div class="audit-card">
                    <div class="audit-header">
                        {row['action_type']} — {row['employee_id']}
                    </div>
                    <div class="audit-meta">
                        User: {row['user_role']} · Waktu: {row['action_time'][11:19]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander("Detail"):
                before = safe_json(row["before_data"])
                after = safe_json(row["after_data"])

                if row["action_type"] == "INSERT":
                    render_insert(after)
                else:
                    render_diff(before, after)


