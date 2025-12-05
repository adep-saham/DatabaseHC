import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import ast
from db import get_conn

# ======================
# SAFETY JSON PARSER
# ======================
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


# ======================
# BUILD DIFF LIST
# ======================
def build_diffs(before, after):
    fields = sorted(set(before.keys()) | set(after.keys()))
    diffs = []
    for f in fields:
        if before.get(f) != after.get(f):
            diffs.append({"field": f, "before": before.get(f), "after": after.get(f)})
    return diffs


# ======================
# MINIMAL TABLE (BEFORE | AFTER)
# ======================
def render_diff(before, after):
    diffs = build_diffs(before, after)

    if not diffs:
        st.info("Tidak ada perubahan field.")
        return

    st.markdown("### Perubahan Field:")

    # Build full HTML table
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
            font-weight: 600;
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


# ======================
# INSERT DATA RENDERING
# ======================
def render_insert(after):
    st.markdown("### Data Baru:")
    for k, v in after.items():
        st.markdown(f"**{k}:** {v}")


# ======================
# MAIN AUDIT TRAIL UI
# ======================
def render_audit():
    st.subheader("Audit Trail")

    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", conn)
    conn.close()

    if df.empty:
        st.info("Belum ada log.")
        return

    df["date"] = df["action_time"].str[:10]

    NUM_COLS = 4  # jumlah card per baris

    for date, group in df.groupby("date"):
        st.markdown(f"### {date}")

        rows = group.to_dict("records")

        # Render grid card
        for i in range(0, len(rows), NUM_COLS):
            cols = st.columns(NUM_COLS)

            for idx, row in enumerate(rows[i:i+NUM_COLS]):
                with cols[idx]:
                    # CARD
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

                    # TITLE
                    st.markdown(
                        f"<div style='font-weight:600; font-size:14px;'>{row['action_type']} — {row['employee_id']}</div>",
                        unsafe_allow_html=True
                    )

                    # USER INFO
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
                            render_insert(after)
                        else:
                            render_diff(before, after)

                    # CLOSE CARD
                    st.markdown("</div>", unsafe_allow_html=True)
