import streamlit as st
import pdfplumber
import docx
import re
from openai import OpenAI

# ---------- PAGE ----------
st.set_page_config(layout="wide")

# ---------- OPENAI (SAFE) ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
st.markdown("""
<style>
body {background-color: #f9fafb;}
.title {
    text-align:center;
    font-size:34px;
    font-weight:700;
}
.subtitle {
    text-align:center;
    color:#6b7280;
    margin-bottom:25px;
}
.card {
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.05);
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Resume Analyzer Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered resume improvement tool</div>', unsafe_allow_html=True)

# ---------- FILE ----------
uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

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
    return text

# ---------- AI FUNCTION ----------
def ai_improve_line(line):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Improve this sentence using strong action verbs and make it impactful."},
                {"role": "user", "content": line}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except:
        return None

# ---------- ANALYSIS ----------
def analyze(text):
    text_lower = text.lower()

    scores = {}
    suggestions = {}
    reasons = {}

    # EDUCATION
    score = 7
    reason = []
    sug = []

    if "college" not in text_lower:
        score -= 2
        reason.append("College not mentioned clearly")
        sug.append("Add full college/university name")

    if "%" not in text_lower and "cgpa" not in text_lower:
        score -= 2
        reason.append("Marks/CGPA missing")
        sug.append("Mention percentage or CGPA")

    scores["Education"] = max(min(score, 10), 3)
    reasons["Education"] = reason
    suggestions["Education"] = sug

    # EXPERIENCE
    score = 7
    reason = []
    sug = []

    if "experience" not in text_lower:
        score -= 2
        reason.append("Experience section missing")
        sug.append("Add Work Experience section")

    if not re.search(r"\b(managed|led|developed)\b", text_lower):
        score -= 2
        reason.append("Weak action words used")
        sug.append("Use strong verbs like managed, led, developed")

    scores["Experience"] = max(min(score, 10), 3)
    reasons["Experience"] = reason
    suggestions["Experience"] = sug

    # ACHIEVEMENTS
    score = 6
    reason = []
    sug = []

    if not re.search(r"\d+%|\d+", text_lower):
        score -= 3
        reason.append("No measurable achievements")
        sug.append("Add numbers like 20%, 50%, etc.")

    scores["Achievements"] = max(min(score, 10), 3)
    reasons["Achievements"] = reason
    suggestions["Achievements"] = sug

    # SKILLS
    score = 7
    reason = []
    sug = []

    if "skills" not in text_lower:
        score -= 2
        reason.append("Skills section missing")
        sug.append("Add a proper skills section")

    scores["Skills"] = max(min(score, 10), 3)
    reasons["Skills"] = reason
    suggestions["Skills"] = sug

    # LANGUAGE
    score = 8
    reason = []
    sug = []

    weak = re.findall(r"\b(responsible|worked|helped|handled)\b", text_lower)
    if len(weak) > 3:
        score -= 3
        reason.append("Too many weak words")
        sug.append("Replace weak words with strong action verbs")

    scores["Language"] = max(min(score, 10), 3)
    reasons["Language"] = reason
    suggestions["Language"] = sug

    return scores, suggestions, reasons

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)

    scores, suggestions, reasons = analyze(text)

    total = sum(scores.values())
    percent = int((total / 50) * 100)

    # SCORE
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Overall Score")
    st.progress(percent)
    st.write(f"### {percent}/100")
    st.markdown('</div>', unsafe_allow_html=True)

    # BREAKDOWN
    st.subheader("📌 Section Breakdown")
    cols = st.columns(5)

    for i, (k, v) in enumerate(scores.items()):
        with cols[i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{k}**")
            st.progress(v * 10)
            st.write(f"{v}/10")
            st.markdown('</div>', unsafe_allow_html=True)

    # DETAILS
    st.markdown("## 💡 Detailed Feedback")

    for section in scores:
        st.markdown(f"### 🔹 {section}")

        if reasons[section]:
            st.write("❌ Why:")
            for r in reasons[section]:
                st.write(f"- {r}")

        if suggestions[section]:
            st.write("💡 Fix:")
            for s in suggestions[section]:
                st.code(s)

    # AI IMPROVEMENTS
    st.markdown("## ✨ AI Improved Sentences")

    for line in text.split("\n"):
        if len(line.strip()) > 20 and re.search(r"\b(responsible|handled|worked|helped)\b", line.lower()):
            improved = ai_improve_line(line)

            if improved:
                st.write("**Original:**")
                st.code(line)

                st.write("**Improved:**")
                st.code(improved)
