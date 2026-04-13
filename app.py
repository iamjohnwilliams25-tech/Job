import streamlit as st
import pdfplumber
import docx
import re
from openai import OpenAI

# ---------- PAGE CONFIG ----------
st.set_page_config(layout="wide")

# ---------- OPENAI ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI DESIGN ----------
st.markdown("""
<style>
body {background-color: #f9fafb;}
.title {
    text-align:center;
    font-size:34px;
    font-weight:700;
    margin-bottom:5px;
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
.section {
    font-size:20px;
    font-weight:600;
    margin-top:25px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Resume Analyzer Pro (AI Powered)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Get smart insights & AI-powered improvements</div>', unsafe_allow_html=True)

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

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

# ---------- AI IMPROVEMENT ----------
def ai_improve_line(line):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Improve the sentence using strong action words and make it impactful."},
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
    edu_score = 7
    edu_reason = []
    edu_sug = []

    if "college" not in text_lower:
        edu_score -= 2
        edu_reason.append("College not clearly mentioned")
        edu_sug.append("Add full college/university name")

    if "%" not in text_lower and "cgpa" not in text_lower:
        edu_score -= 2
        edu_reason.append("Marks/CGPA missing")
        edu_sug.append("Mention your percentage or CGPA")

    scores["Education"] = max(min(edu_score, 10), 3)
    reasons["Education"] = edu_reason
    suggestions["Education"] = edu_sug

    # EXPERIENCE
    exp_score = 7
    exp_reason = []
    exp_sug = []

    if "experience" not in text_lower:
        exp_score -= 2
        exp_reason.append("Experience section not clear")
        exp_sug.append("Add a proper Work Experience section")

    if not re.search(r"\b(managed|led|developed)\b", text_lower):
        exp_score -= 2
        exp_reason.append("Weak action words used")
        exp_sug.append("Use strong verbs like managed, led, developed")

    scores["Experience"] = max(min(exp_score, 10), 3)
    reasons["Experience"] = exp_reason
    suggestions["Experience"] = exp_sug

    # ACHIEVEMENTS
    ach_score = 6
    ach_reason = []
    ach_sug = []

    if not re.search(r"\d+%|\d+", text_lower):
        ach_score -= 3
        ach_reason.append("No measurable achievements")
        ach_sug.append("Add numbers (e.g., improved by 20%)")

    scores["Achievements"] = max(min(ach_score, 10), 3)
    reasons["Achievements"] = ach_reason
    suggestions["Achievements"] = ach_sug

    # SKILLS
    skill_score = 7
    skill_reason = []
    skill_sug = []

    if "skills" not in text_lower:
        skill_score -= 2
        skill_reason.append("Skills section missing")
        skill_sug.append("Add a dedicated skills section")

    scores["Skills"] = max(min(skill_score, 10), 3)
    reasons["Skills"] = skill_reason
    suggestions["Skills"] = skill_sug

    # LANGUAGE
    lang_score = 8
    lang_reason = []
    lang_sug = []

    weak_words = re.findall(r"\b(responsible|worked|helped|handled)\b", text_lower)
    if len(weak_words) > 3:
        lang_score -= 3
        lang_reason.append("Too many weak words")
        lang_sug.append("Replace weak words with strong action verbs")

    scores["Language"] = max(min(lang_score, 10), 3)
    reasons["Language"] = lang_reason
    suggestions["Language"] = lang_sug

    return scores, suggestions, reasons

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)

    scores, suggestions, reasons = analyze(text)

    total = sum(scores.values())
    percent = int((total / 50) * 100)

    # ---------- SCORE ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Overall Score")
    st.progress(percent)
    st.write(f"### {percent}/100")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- SECTION SCORES ----------
    st.subheader("📌 Section Breakdown")

    cols = st.columns(5)
    for i, (k, v) in enumerate(scores.items()):
        with cols[i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{k}**")
            st.progress(v * 10)
            st.write(f"{v}/10")
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------- DETAILED FEEDBACK ----------
    st.markdown("## 💡 Detailed Feedback")

    for section in scores:
        st.markdown(f"### 🔹 {section}")

        if reasons[section]:
            st.write("❌ **Why:**")
            for r in reasons[section]:
                st.write(f"- {r}")

        if suggestions[section]:
            st.write("💡 **Fix this:**")
            for s in suggestions[section]:
                st.code(s)

    # ---------- AI IMPROVEMENTS ----------
    st.markdown("## ✨ AI Improved Sentences")

    for line in text.split("\n"):
        if len(line.strip()) > 20 and re.search(r"\b(responsible|handled|worked|helped)\b", line.lower()):
            improved = ai_improve_line(line)

            if improved:
                st.write("**Original:**")
                st.code(line)

                st.write("**Improved:**")
                st.code(improved)
