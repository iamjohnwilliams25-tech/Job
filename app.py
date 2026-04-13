import streamlit as st
import pdfplumber
import docx
from openai import OpenAI
import json

# ---------- PAGE CONFIG ----------
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- HIDE STREAMLIT UI COMPLETELY ----------
hide_st_style = """
<style>
/* Hide Streamlit default menu + footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide top right toolbar (NEW UI FIX) */
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}
[data-testid="stDeployButton"] {display: none;}
button[kind="header"] {display: none;}

/* Remove extra top spacing */
.block-container {
    padding-top: 1rem;
}
</style>
"""

st.markdown(hide_st_style, unsafe_allow_html=True)

# ---------- API ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
