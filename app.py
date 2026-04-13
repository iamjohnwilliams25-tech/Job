import streamlit as st
import pdfplumber
import docx
import re

st.set_page_config(layout="wide")

# ---------- CLEAN CSS ----------
st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}
.card {
    padding: 18px;
    border-radius: 12px;
    background: #f8fafc;
    margin-bottom: 12px;
    border: 1px solid #e2e8f0;
}
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📄 Resume Analyzer Pro</div>', unsafe_allow_html=True)
st.write("Upload your resume and get actionable insights")

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

# ---------- ANALYSIS ----------
def analyze(text):
    scores = {}
    suggestions = {}

    # EDUCATION
    edu_score = 5
    edu_sug = []
    if "college" in text or "university" in text:
        edu_score += 3
    else:
        edu_sug.append("Add proper college/university name")

    if "%" in text or "cgpa" in text:
        edu_score += 2
    else:
        edu_sug.append("Mention your percentage or CGPA")

    scores["Education"] = min(edu_score, 10)
    suggestions["Education"] = edu_sug

    # EXPERIENCE
    exp_score = 5
    exp_sug = []
    if "experience" in text:
        exp_score += 2
    else:
        exp_sug.append("Add a clear 'Work Experience' section")

    if re.search(r"\b(managed|led|developed)\b", text):
        exp_score += 3
    else:
        exp_sug.append("Use strong action words like 'managed', 'led', 'developed'")

    scores["Experience"] = min(exp_score, 10)
    suggestions["Experience"] = exp_sug

    # ACHIEVEMENTS
    ach_score = 3
    ach_sug = []
    if re.search(r"\d+%", text):
        ach_score += 5
    else:
        ach_sug.append("Add measurable achievements (e.g., increased sales by 20%)")

    scores["Achievements"] = min(ach_score, 10)
    suggestions["Achievements"] = ach_sug

    # SKILLS
    skill_score = 4
    skill_sug = []
    if "skills" in text:
        skill_score += 4
    else:
        skill_sug.append("Add a dedicated Skills section")

    scores["Skills"] = min(skill_score, 10)
    suggestions["Skills"] = skill_sug

    # LANGUAGE
    lang_score = 6
    lang_sug = []
    weak = re.findall(r"\b(responsible|worked|helped)\b", text)
    if len(weak) > 5:
        lang_score -= 2
        lang_sug.append("Avoid weak words like 'responsible', 'worked', 'helped'")

    scores["Language"] = max(min(lang_score, 10), 3)
    suggestions["Language"] = lang_sug

    return scores, suggestions

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)

    scores, suggestions = analyze(text)
    total = sum(scores.values())
    percent = int((total / 50) * 100)

    # ---------- SCORE ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Overall Score")
    st.progress(percent)
    st.write(f"### {percent}/100")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- SECTION SCORES ----------
    st.subheader("📌 Section Scores")

    cols = st.columns(5)
    for i, (k, v) in enumerate(scores.items()):
        with cols[i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{k}**")
            st.progress(v * 10)
            st.write(f"{v}/10")
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------- SUGGESTIONS ----------
    st.markdown('<div class="section-title">💡 Improvement Suggestions</div>', unsafe_allow_html=True)

    for section, sug_list in suggestions.items():
        if sug_list:
            st.markdown(f"### 🔹 {section}")

            for s in sug_list:
                st.code(s)
