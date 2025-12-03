import streamlit as st
import pandas as pd
import json
from db import get_conn
from utils import diff_changes

def render_audit():
    st.subheader("🕒 Audit Trail")

    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY action_time DESC", get_conn())

    if df.empty:
        st.info("Belum ada log.")
        return

    for _, row in df.iterrows():
        st.write("---")
        st.write(
            f"🕒 {row['action_time']} | 👤 {row['user_role']} "
            f"| 🔧 {row['action_type']} | 🆔 {row['employee_id']}"
        )

        with st.expander("Detail"):
            try:
                before = json.loads(row["before_data"]) if row["before_data"] else {}
                after = json.loads(row["after_data"]) if row["after_data"] else {}

                changes = diff_changes(before, after)

                if not changes:
                    st.info("Tidak ada perubahan field.")
                else:
                    for c in changes:
                        st.write(f"**{c['field']}**: `{c['before']}` → `{c['after']}`")

            except:
                st.caption(row["detail"])
