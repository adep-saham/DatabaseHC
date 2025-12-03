import streamlit as st

from db import init_db
from ui_form import render_form
from ui_screening import render_screening
from ui_audit import render_audit
from ui_quality import render_quality

st.set_page_config(page_title="HC Employee Database", layout="wide")

st.title("📋 HC Employee Database – HC System & Data Management")

# Init DB
init_db()

# Role selector
role = st.sidebar.selectbox(
    "Role",
    ["Viewer", "HR Admin", "HC System Bureau Head"],
    index=1
)

# Main Menu
menu = st.sidebar.radio(
    "Menu",
    [
        "Input / Update Data Pegawai",
        "Screening Kandidat",
        "Audit Trail",
        "Data Quality Dashboard"
    ]
)

if menu == "Input / Update Data Pegawai":
    render_form(role)

elif menu == "Screening Kandidat":
    render_screening()

elif menu == "Audit Trail":
    render_audit()

elif menu == "Data Quality Dashboard":
    render_quality()
