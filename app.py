import streamlit as st
import os
import sqlite3

from db import init_db
from ui_form import render_form
from ui_audit import render_audit
from ui_screening import render_screening
from ui_quality import render_quality
from generate_dummy_data import generate_dummy_data


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="HC Employee DB", layout="wide")


# ==========================================================
# AUTO UPGRADE AUDIT TABLE (ADD username COLUMN IF NEEDED)
# ==========================================================
def auto_upgrade_audit_table():
    conn = sqlite3.connect("hc_employee.db")
    cur = conn.cursor()

    # cek struktur tabel audit_log
    cur.execute("PRAGMA table_info(audit_log)")
    columns = [row[1] for row in cur.fetchall()]

    # jika kolom username belum ada → tambahkan
    if "username" not in columns:
        cur.execute("ALTER TABLE audit_log ADD COLUMN username TEXT;")
        conn.commit()

    conn.close()

auto_upgrade_audit_table()


# ==========================================================
# SESSION LOGIN STATE
# ==========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ==========================================================
# ROLE MAPPING (username → role)
# ==========================================================
USER_ROLE_MAP = {
    "adep": "HC System Bureau Head",
    # tambahkan user lain jika diperlukan:
    # "budi": "HR Admin",
    # "siti": "Viewer",
}

DEFAULT_ROLE = "Viewer"


# ==========================================================
# LOGIN PAGE
# ==========================================================
def login_page():
    st.title("🔐 Login HC Employee System")
    st.write("Masukkan username untuk mengakses aplikasi.")

    username_input = st.text_input("Username", key="login_username")

    if st.button("LOGIN"):
        if username_input.strip() == "":
            st.error("Username tidak boleh kosong!")
        else:
            st.session_state.username = username_input.strip().lower()
            st.session_state.logged_in = True
            st.rerun()


# ==========================================================
# LOGOUT
# ==========================================================
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()


# ==========================================================
# MAIN MENU PAGE
# ==========================================================
def main_menu():

    username = st.session_state.username
    role = USER_ROLE_MAP.get(username, DEFAULT_ROLE)

    # memastikan DB ada
    init_db()

    # ================ SIDEBAR USER INFO ==================
    st.sidebar.title("User Info")
    st.sidebar.success(f"👤 Login sebagai: {username}")
    st.sidebar.info(f"Role: **{role}**")

    if st.sidebar.button("LOGOUT"):
        logout()

    st.sidebar.title("Menu")
    menu = st.sidebar.radio(
        "Pilih Halaman:",
        [
            "Input / Update Data Pegawai",
            "Screening Kandidat / Talent Readiness",
            "Data Quality Dashboard",
            "Audit Trail"
        ]
    )

    # ================ HC SYSTEM ADMIN TOOLS ==================
    if role == "HC System Bureau Head":
        st.sidebar.markdown("### 🛠 Database Tools")

        if st.sidebar.button("🧨 RESET DATABASE"):
            try:
                os.remove("hc_employee.db")
            except:
                pass
            init_db()
            st.sidebar.success("Database berhasil direset!")

        if st.sidebar.button("🚀 Generate Dummy Employees"):
            msg = generate_dummy_data(15)
            st.sidebar.success(msg)

        if st.sidebar.button("♻ Optimize Database"):
            conn = sqlite3.connect("hc_employee.db")
            conn.execute("VACUUM")
            conn.close()
            st.sidebar.success("Database optimized!")


    # ===================== PAGE ROUTER =====================

    if menu == "Input / Update Data Pegawai":
        render_form(role, username)

    elif menu == "Screening Kandidat / Talent Readiness":
        render_screening()

    elif menu == "Data Quality Dashboard":
        render_quality()

    elif menu == "Audit Trail":
        render_audit()


# ==========================================================
# RUN APPLICATION
# ==========================================================
if not st.session_state.logged_in:
    login_page()
else:
    main_menu()
