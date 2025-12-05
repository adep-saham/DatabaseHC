import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import ast
from db import get_conn


# ======================================================
# SAFE JSON CONVERTER
# ======================================================
def safe_json(raw):
    if raw in (None, "", "null"):
        return {}
    try:
        return json.loads(raw)
    except:
        try:
            return ast.literal_eval(raw)
        except:
            return {}


# ======================================================
# BUILD DIFF FIELDS
# ======================================================
def build_diffs(before, after):
    fields = sorted(set(before.keys()) | set(after.keys()))
    diffs = []
    for f in fields:
        if before.get(f) != after.get(f):
            diffs.append({
                "field": f,
                "before": before.get(f),
                "after": after.get(f)
            })
    return diffs


# ======================================================
# RENDER DIFF (2 Kolom) + info user pengubah
# ======================================================
def render_diff(before, after, username, role, action_time):

    st.markdown("### Perubahan Field:")

    # Tambahkan informasi siapa yang mengubah
    st.markdown(f"""
        <div style='font-size:13px; margin-bottom:14px; line-height:1.4;'>
            <b>User pengubah:</b> {username} ({role})<br>
            <b>Waktu update:</b> {action_time[11:19]}
        </div>
    """, unsafe_allow_html=True)

    diffs = build_diffs(before, after)
    if not diffs:
        st.info("Tidak ada perubahan field.")
        return

    # Tabel HTML
    table_html = """
    <html>
    <head>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th {
            background: #f2f2f2;
            padding: 6px 8px;
            border-bottom: 1px solid #ccc;
            text-align: left;
        }
        td {
            padding: 6px 8px;
            border-bottom: 1px solid #eee;
        }
    </style>
    </head>
    <body>
    <table>
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

    table_html += """
    </table>
    </body>
    </html>
    """

    components.html(table_html, height=300, scrolling=True)


# ======================================================
# RENDER INSERT DATA BARU
# ======================================================
def render_insert(after, username, role, action_time):

    st.markdown("### Data Baru:")

    st.markdown(f"""
        <div style='font-size:13px; margin-bottom:14px; line-height:1.4;'>
            <b>User input:</b> {username} ({role})<br>
            <b>Waktu input:</b> {action_time[11:19]}
        </div>
    """, unsafe_allow_html=True)

    for k, v in after.items():
        st.markdown(f"**{k}**: {v}")


# ======================================================
# RENDER AUDIT TRAIL (GRID CARD)
# ======================================================
def render_audit():

    st.subheader("🕒 Audit Trail")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada log.")
        return

    df["date"] = df["action_time"].str[:10]

    NUM_COLS = 4  # jumlah card per baris

    for date, group in df.groupby("date"):
        st.markdown(f"## 📅 {date}")

        rows = group.to_dict("records")

        for i in range(0, len(rows), NUM_COLS):
            cols = st.columns(NUM_COLS)

            for idx, row in enumerate(rows[i:i+NUM_COLS]):

                with cols[idx]:

                    # CARD HEADER
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
                        f"<div style='font-weight:600; font-size:14px;'>{row['action_type']} — {row['employee_id']}</div>",
                        unsafe_allow_html=True
                    )

                    # USER metadata
                    st.markdown(
                        f"""
                        <div style='font-size:12px;color:#666;'>
                            User: <b>{row.get('username', 'UNKNOWN')}</b> ({row['user_role']})<br>
                            Waktu: {row['action_time'][11:19]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # DETAIL EXPANDER
                    with st.expander("Detail"):

                        before = safe_json(row["before_data"])
                        after = safe_json(row["after_data"])

                        if row["action_type"] == "INSERT":
                            render_insert(
                                after,
                                row.get("username", "UNKNOWN"),
                                row["user_role"],
                                row["action_time"]
                            )
                        else:
                            render_diff(
                                before,
                                after,
                                row.get("username", "UNKNOWN"),
                                row["user_role"],
                                row["action_time"]
                            )

                    st.markdown("</div>", unsafe_allow_html=True)
