import streamlit as st
import pdfplumber
import docx
import re
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: white;
}
.big-title {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(to right, #6366f1, #9333ea);
    -webkit-background-clip: text;
    color: transparent;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background: #1e293b;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🚀 Resume Analyzer Pro</div>', unsafe_allow_html=True)
st.write("### Upload your resume and get deep insights")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

# ---------- TEXT EXTRACTION ----------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    else:
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.lower()

# ---------- SCORING ----------
def score_resume(text):
    edu = 7 if "college" in text else 4
    exp = 8 if "experience" in text else 5
    ach = 6 if re.search(r"\d+", text) else 3
    skills = 7 if "skills" in text else 4
    fmt = 6
    lang = 6

    return {
        "Education": edu,
        "Experience": exp,
        "Achievements": ach,
        "Skills": skills,
        "Formatting": fmt,
        "Language": lang
    }

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)

    scores = score_resume(text)

    total = sum(scores.values())
    percent = int((total / 60) * 100)

    # ---------- SCORE CARD ----------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Overall Score")
        st.progress(percent)
        st.write(f"### {percent}/100")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚠️ Key Insight")
        if percent < 60:
            st.write("Your resume needs strong improvement")
        elif percent < 80:
            st.write("Good resume, but can be improved")
        else:
            st.write("Strong resume 👍")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- SECTION CARDS ----------
    st.subheader("📈 Section Analysis")

    cols = st.columns(3)
    for i, (k, v) in enumerate(scores.items()):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"### {k}")
            st.progress(v * 10)
            st.write(f"{v}/10")
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------- RADAR CHART ----------
    st.subheader("📊 Performance Graph")

    labels = list(scores.keys())
    values = list(scores.values())

    values += values[:1]
    labels += labels[:1]

    fig, ax = plt.subplots()
    ax.plot(values)
    ax.fill(values, alpha=0.3)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)

    st.pyplot(fig)
