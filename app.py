import streamlit as st
import pdfplumber
import docx
import re
from openai import OpenAI

st.set_page_config(layout="wide")

# ---------- OPENAI ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
st.markdown("""
<style>
body {background:#f5f7fb;}
.title {text-align:center;font-size:34px;font-weight:700;}
.subtitle {text-align:center;color:#6b7280;margin-bottom:20px;}
.card {
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0 4px 12px rgba(0,0,0,0.05);
    margin-bottom:15px;
}
.section {font-size:22px;font-weight:600;margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Resume Analyzer Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered professional resume upgrade</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

# ---------- EXTRACT TEXT ----------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    else:
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# ---------- SPLIT SECTIONS ----------
def split_sections(text):
    sections = {
        "Education": "",
        "Experience": "",
        "Skills": "",
        "Other": ""
    }

    current = "Other"
    for line in text.split("\n"):
        l = line.lower()

        if "education" in l:
            current = "Education"
        elif "experience" in l:
            current = "Experience"
        elif "skills" in l:
            current = "Skills"

        sections[current] += line + "\n"

    return sections

# ---------- AI REWRITE ----------
def rewrite_section(section_text, section_name):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a top-tier resume writer. Rewrite the {section_name} section professionally with strong action verbs, clear bullet points, and corporate tone. Keep it realistic and not fake."
                },
                {
                    "role": "user",
                    "content": section_text
                }
            ],
            temperature=0.6
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"

# ---------- SCORING ----------
def score_section(text):
    score = 6
    if re.search(r"\d+%|\d+", text):
        score += 2
    if re.search(r"\b(managed|led|developed)\b", text.lower()):
        score += 2
    return min(score, 10)

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)
    sections = split_sections(text)

    # ---------- SCORES ----------
    st.markdown("## 📊 Resume Score")

    cols = st.columns(4)
    scores = {}

    for i, (sec, content) in enumerate(sections.items()):
        s = score_section(content)
        scores[sec] = s

        with cols[i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{sec}**")
            st.progress(s * 10)
            st.write(f"{s}/10")
            st.markdown('</div>', unsafe_allow_html=True)

    total = int(sum(scores.values()) / len(scores) * 10)
    st.success(f"Overall Score: {total}/100")

    # ---------- AI IMPROVED SECTIONS ----------
    st.markdown("## ✨ AI Professional Resume Upgrade")

    for sec, content in sections.items():
        if len(content.strip()) > 30:

            st.markdown(f"### 🔹 {sec}")

            improved = rewrite_section(content, sec)

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Original**")
                st.code(content)

            with col2:
                st.write("**Improved (Professional)**")
                st.code(improved)
