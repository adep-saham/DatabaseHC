import streamlit as st
import pandas as pd
import json
import ast
from db import get_conn


# =========================================================
# Helper: aman membaca JSON / dict-string
# =========================================================
def safe_json(raw):
    if raw in [None, "", "null"]:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        try:
            return ast.literal_eval(raw)
        except Exception:
            return {}


# =========================================================
# Build diff antara before & after
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


def render_insert_table(after: dict):
    """Untuk INSERT / INSERT_DUMMY: tampilkan semua field sebagai 'After'."""
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
