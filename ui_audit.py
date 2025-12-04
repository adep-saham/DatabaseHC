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

    # CSS untuk grid card
    st.markdown("""
    <style>
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 12px;
            margin-bottom: 25px;
        }
        .grid-card {
            border: 1px solid #DDD;
            border-radius: 6px;
            padding: 10px 14px;
            background: #FFFFFF;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .card-title {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }
        .card-meta {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Render per tanggal
    for date, group in df.groupby("date"):
        st.markdown(f"### {date}")

        # Start grid container
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)

        for _, row in group.iterrows():
            card_html = f"""
            <div class="grid-card">
                <div class="card-title">{row['action_type']} — {row['employee_id']}</div>
                <div class="card-meta">User: {row['user_role']} · Waktu: {row['action_time'][11:19]}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # expander di bawah card (tetap Streamlit)
            with st.expander("Detail"):
                before = safe_json(row["before_data"])
                after = safe_json(row["after_data"])

                if row["action_type"] == "INSERT":
                    render_insert(after)
                else:
                    render_diff(before, after)

        # End grid
        st.markdown('</div>', unsafe_allow_html=True)



