import streamlit as st
import os

from db import init_db
from ui_form import render_form
from ui_audit import render_audit
from ui_screening import render_screening
from ui_quality import render_quality
from generate_dummy_data import generate_dummy_data

st.set_page_config(page_title="HC Employee DB", layout="wide")

st.title("📋 HC Employee Database – HC System & Data Management")

# Init database (ensure tables exist)
init_db()

# Role selection
role = st.sidebar.selectbox("Role", ["Viewer", "HR Admin", "HC System Bureau Head"])

# Main Navigation
menu = st.sidebar.radio(
    "Menu",
    [
        "Input / Update Data Pegawai",
        "Screening Kandidat / Talent Readiness",
        "Data Quality Dashboard",
        "Audit Trail"
    ]
)

# ======================
# SIMPLE LOGIN SYSTEM
# ======================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.sidebar.title("User Login")

if not st.session_state.logged_in:
    # Input username sebelum login
    username_input = st.sidebar.text_input("Username:", key="username_input")

    # Tombol LOGIN
    if st.sidebar.button("LOGIN"):
        if username_input.strip() == "":
            st.sidebar.error("Username tidak boleh kosong.")
        else:
            st.session_state.username = username_input.strip()
            st.session_state.logged_in = True
            st.sidebar.success(f"Login berhasil sebagai {st.session_state.username}")
else:
    # Jika sudah login → tampilkan info & tombol logout
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()



# ============================
# SPECIAL TOOLS for HC SYSTEM
# ============================
if role == "HC System Bureau Head":

    st.sidebar.markdown("### 🛠 Database Tools")

    # RESET DB
    if st.sidebar.button("🧨 RESET DATABASE (Hapus & Buat Baru)"):
        try:
            os.remove("hc_employee.db")
        except:
            pass
        init_db()
        st.sidebar.success("Database berhasil direset!")

    # Generate Dummy
    if st.sidebar.button("🚀 Generate Dummy Employees"):
        msg = generate_dummy_data(15)
        st.sidebar.success(msg)

    # Optimize DB (VACUUM)
    if st.sidebar.button("♻ Optimize Database"):
        import sqlite3
        conn = sqlite3.connect("hc_employee.db")
        conn.execute("VACUUM")
        conn.close()
        st.sidebar.success("Database optimized!")

# Main Render
if menu == "Input / Update Data Pegawai":
    render_form(role)

elif menu == "Screening Kandidat / Talent Readiness":
    render_screening()

elif menu == "Data Quality Dashboard":
    render_quality()

elif menu == "Audit Trail":
    render_audit()


