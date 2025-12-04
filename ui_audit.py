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

    st.markdown("### Perubahan Field:")

    # CSS untuk tabel
    st.markdown("""
    <style>
        .diff-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }
        .diff-table th {
            text-align: left;
            padding: 6px 8px;
            background: #f2f2f2;
            border-bottom: 1px solid #ccc;
            font-weight: 600;
        }
        .diff-table td {
            padding: 6px 8px;
            border-bottom: 1px solid #eee;
        }
    </style>
    """, unsafe_allow_html=True)

    # Build HTML string utuh (penting!)
    table_html = """
    <table class="diff-table">
        <tr>
            <th>Field</th>
            <th>Before</th>
            <th>After</th>
        </tr>
    """

    for d in diffs:
        table_html += f"""
        <tr>
            <td><b>{d['field']}</b></td>
            <td>{d['before']}</td>
            <td>{d['after']}</td>
        </tr>
        """

    table_html += "</table>"

    # Render sebagai HTML murni
    st.markdown(table_html, unsafe_allow_html=True)




def render_insert(after):
    st.markdown("<div style='font-weight:600; margin-bottom:6px;'>Data Baru:</div>", unsafe_allow_html=True)

    for k, v in after.items():
        st.markdown(f"""
        <div style="margin-bottom:8px; padding-left:4px;">
            <div style="font-size:13px; font-weight:600;">{k}</div>
            <div style="font-size:12px; color:#000;">{v}</div>
        </div>
        """, unsafe_allow_html=True)


def render_audit():
    st.subheader("Audit Trail")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada log.")
        return

    df["date"] = df["action_time"].str[:10]

    # CONFIG: jumlah kolom (4 sama seperti contoh Anda)
    NUM_COLS = 4

    for date, group in df.groupby("date"):
        st.markdown(f"### {date}")

        rows = group.to_dict("records")

        # Buat grid berdasarkan jumlah kolom
        for i in range(0, len(rows), NUM_COLS):
            cols = st.columns(NUM_COLS)

            for idx, row in enumerate(rows[i:i+NUM_COLS]):
                with cols[idx]:
                    st.markdown(
                        """
                        <div style="
                            border:1px solid #DDD;
                            padding:10px 14px;
                            border-radius:6px;
                            background:#FFF;
                            margin-bottom:8px;
                        ">
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"**{row['action_type']} — {row['employee_id']}**  \n"
                        f"<span style='font-size:12px;color:#666;'>User: {row['user_role']} · Waktu: {row['action_time'][11:19]}</span>",
                        unsafe_allow_html=True
                    )

                    with st.expander("Detail"):
                        before = safe_json(row["before_data"])
                        after = safe_json(row["after_data"])
                        if row["action_type"] == "INSERT":
                            render_insert(after)
                        else:
                            render_diff(before, after)

                    st.markdown("</div>", unsafe_allow_html=True)








