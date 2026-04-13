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
body {background:#f4f6fb;}
.title {text-align:center;font-size:34px;font-weight:700;}
.name {text-align:center;font-size:26px;font-weight:600;margin-top:10px;}
.card {
    background:white;
    padding:15px;
    border-radius:10px;
    box-shadow:0 4px 10px rgba(0,0,0,0.05);
    margin-bottom:10px;
}
.section-title {
    font-size:20px;
    font-weight:700;
    margin-top:20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Resume Analyzer Pro</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

# ---------- EXTRACT ----------
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

# ---------- NAME DETECTION ----------
def get_name(text):
    lines = text.split("\n")
    for line in lines[:5]:
        if len(line.strip()) > 3 and len(line.split()) <= 4:
            return line.strip()
    return "Candidate"

# ---------- SCORING ----------
def analyze(text):
    text_lower = text.lower()

    scores = {}
    reasons = {}
    suggestions = {}

    # EXPERIENCE
    score = 6
    reason = []
    sug = []

    if not re.search(r"\b(managed|led|developed)\b", text_lower):
        score -= 2
        reason.append("Weak action words")
        sug.append("Use strong verbs like managed, led, developed")

    scores["Experience"] = score
    reasons["Experience"] = reason
    suggestions["Experience"] = sug

    # SKILLS
    score = 7
    reason = []
    sug = []

    if "skills" not in text_lower:
        score -= 2
        reason.append("Skills section missing")
        sug.append("Add a proper skills section")

    scores["Skills"] = score
    reasons["Skills"] = reason
    suggestions["Skills"] = sug

    # ACHIEVEMENTS
    score = 6
    reason = []
    sug = []

    if not re.search(r"\d+%|\d+", text_lower):
        score -= 2
        reason.append("No measurable results")
        sug.append("Add numbers like 20%, 30% impact")

    scores["Achievements"] = score
    reasons["Achievements"] = reason
    suggestions["Achievements"] = sug

    return scores, reasons, suggestions

# ---------- AI RESUME ----------
def generate_resume(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Rewrite this resume professionally:
- Extract candidate name
- Proper sections with bold headings
- Bullet points
- Strong corporate tone
- Clean formatting
"""
                },
                {"role": "user", "content": text}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)
    name = get_name(text)

    st.markdown(f'<div class="name">{name}</div>', unsafe_allow_html=True)

    scores, reasons, suggestions = analyze(text)

    # ---------- SCORE DASHBOARD ----------
    st.markdown("## 📊 Score Overview")

    cols = st.columns(3)

    for i, (sec, val) in enumerate(scores.items()):
        with cols[i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{sec}**")
            st.progress(val * 10)
            st.write(f"{val}/10")

            if reasons[sec]:
                st.write("❌")
                for r in reasons[sec]:
                    st.write(f"- {r}")

            if suggestions[sec]:
                st.write("💡")
                for s in suggestions[sec]:
                    st.code(s)

            st.markdown('</div>', unsafe_allow_html=True)

    total = int(sum(scores.values()) / len(scores) * 10)
    st.success(f"Overall Score: {total}/100")

    # ---------- AI OUTPUT ----------
    st.markdown("## ✨ Professional Resume")

    improved = generate_resume(text)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(improved)
    st.markdown('</div>', unsafe_allow_html=True)
