import streamlit as st
import pandas as pd
import json
import ast
from db import get_conn


# =========================================================
# SAFE JSON PARSER
# =========================================================
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


# =========================================================
# BUILD DIFF
# =========================================================
def build_diffs(before: dict, after: dict):
    fields = sorted(set(before.keys()) | set(after.keys()))
    diffs = []
    for f in fields:
        b = before.get(f)
        a = after.get(f)
        if b != a:
            diffs.append(
                {
                    "field": f,
                    "before": "" if b is None else b,
                    "after": "" if a is None else a,
                }
            )
    return diffs


def render_diff(before: dict, after: dict):
    diffs = build_diffs(before, after)

    if not diffs:
        st.info("Tidak ada perubahan field.")
        return

    st.write("### 🔄 Perubahan Field")

    st.markdown(
        """
    <table style='width:100%;border-collapse:collapse;margin-top:10px;'>
        <tr style='background:#EEE;font-weight:bold;'>
            <td style='padding:8px;border:1px solid #DDD;'>Field</td>
            <td style='padding:8px;border:1px solid #DDD;'>Before</td>
            <td style='padding:8px;border:1px solid #DDD;'>After</td>
        </tr>
    """,
        unsafe_allow_html=True,
    )

    for d in diffs:
        st.markdown(
            f"""
        <tr>
            <td style='padding:8px;border:1px solid #DDD;'>{d['field']}</td>
            <td style='padding:8px;border:1px solid #DDD;color:#B00020;'>{d['before']}</td>
            <td style='padding:8px;border:1px solid #DDD;color:#006400;font-weight:bold;'>{d['after']}</td>
        </tr>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</table>", unsafe_allow_html=True)


# =========================================================
# RENDER INSERT TABLE
# =========================================================
def render_insert_table(after: dict):
    if not after:
        st.info("Tidak ada data untuk ditampilkan.")
        return

    st.write("### 🆕 Data Baru (Insert)")

    st.markdown(
        """
    <table style='width:100%;border-collapse:collapse;margin-top:10px;'>
        <tr style='background:#EEE;font-weight:bold;'>
            <td style='padding:8px;border:1px solid #DDD;'>Field</td>
            <td style='padding:8px;border:1px solid #DDD;'>Value</td>
        </tr>
    """,
        unsafe_allow_html=True,
    )

    for k, v in after.items():
        st.markdown(
            f"""
        <tr>
            <td style='padding:8px;border:1px solid #DDD;'>{k}</td>
            <td style='padding:8px;border:1px solid #DDD;'>{v}</td>
        </tr>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</table>", unsafe_allow_html=True)


# =========================================================
# MAIN AUDIT RENDERER
# =========================================================
def render_audit():
    st.subheader("🕒 Audit Trail (Simple & Powerful)")

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

            st.markdown(
                f"""
            <div style='padding:12px;border:1px solid #DDD;background:#FAFAFA;margin-bottom:6px;'>
                <b>🔧 {row['action_type']}</b> | 🆔 {row['employee_id']}<br>
                👤 {row['user_role']} • 🕒 {row['action_time']}
            </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander("Detail Perubahan"):

                before = safe_json(row.get("before_data"))
                after = safe_json(row.get("after_data"))

                action = str(row["action_type"] or "").upper()

                # INSERT / INSERT_DUMMY
                if action.startswith("INSERT"):
                    render_insert_table(after)
                    continue

                # Jika before/after kosong → tampilkan detail mentah
                if not before and not after:
                    st.warning("Data before/after kosong. Menampilkan detail mentah:")
                    st.code(row.get("detail", ""), language="text")
                    continue

                # UPDATE → tampilkan DIFF
                render_diff(before, after)
