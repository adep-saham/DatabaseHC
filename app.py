import streamlit as st

# =====================================================
# IMPORT HALAMAN-HALAMAN ANDA
# =====================================================
from ui_input_update import render_input_update   # jika berbeda, sesuaikan
from ui_screening import render_screening
from ui_quality import render_quality
from ui_dashboard import render_dashboard
from ui_audit import render_audit


# =====================================================
# SESSION STATE LOGIN
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    st.set_page_config(page_title="Login HC System", layout="centered")

    st.title("🔐 Login HC Employee System")
    st.write("Silakan masukkan username untuk masuk ke aplikasi.")

    username_input = st.text_input("Username", key="login_username")

    if st.button("LOGIN"):
        if username_input.strip() == "":
            st.error("Username tidak boleh kosong!")
        else:
            st.session_state.username = username_input.strip()
            st.session_state.logged_in = True
            st.success(f"Login berhasil! Selamat datang, {username_input}.")
            st.experimental_rerun()


# =====================================================
# LOGOUT FUNGSI
# =====================================================
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()


# =====================================================
# MAIN MENU SETELAH LOGIN
# =====================================================
def main_menu():

    st.sidebar.title("User")
    st.sidebar.success(f"👤 Login sebagai: {st.session_state.username}")

    if st.sidebar.button("LOGOUT"):
        logout()

    st.sidebar.title("Menu")
    menu = st.sidebar.radio(
        "Pilih Halaman:",
        [
            "Input / Update Data Pegawai",
            "Screening Kandidat / Talent Readiness",
            "Data Quality",
            "Dashboard",
            "Audit Trail"
        ]
    )

    # ROUTING KE HALAMAN
    if menu == "Input / Update Data Pegawai":
        render_input_update(st.session_state.username)

    elif menu == "Screening Kandidat / Talent Readiness":
        render_screening(st.session_state.username)

    elif menu == "Data Quality":
        render_quality(st.session_state.username)

    elif menu == "Dashboard":
        render_dashboard(st.session_state.username)

    elif menu == "Audit Trail":
        render_audit()


# =====================================================
# ENTRY POINT APLIKASI
# =====================================================
if not st.session_state.logged_in:
    login_page()
else:
    main_menu()
