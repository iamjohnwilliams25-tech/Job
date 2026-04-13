import streamlit as st
import pdfplumber
import docx
import re
from openai import OpenAI

st.set_page_config(layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
st.markdown("""
<style>
body {background:#f4f6fb;}
.title {text-align:center;font-size:36px;font-weight:800;}
.name {text-align:center;font-size:26px;font-weight:700;margin-bottom:20px;}
.card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 12px rgba(0,0,0,0.06);
    margin-bottom:10px;
}
.red {color:#dc2626;font-weight:700;}
.green {color:#16a34a;font-weight:700;}
.amber {color:#d97706;font-weight:700;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Resume Analyzer Pro MAX</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
job_role = st.text_input("🎯 Enter Target Job Role (e.g. Customer Support Executive, Data Analyst)")

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

# ---------- NAME ----------
def get_name(text):
    for line in text.split("\n")[:8]:
        if line.strip().isupper():
            return line.title()
        if 2 <= len(line.split()) <= 4:
            return line.strip()
    return "Candidate"

# ---------- SECTION DETECTION ----------
def detect_sections(text):
    sections = {
        "Profile": "", "Experience": "", "Education": "",
        "Skills": "", "Achievements": "", "Languages": "",
        "Hobbies": "", "Contact": ""
    }

    current = "Profile"

    for line in text.split("\n"):
        l = line.lower()

        if "experience" in l:
            current = "Experience"
        elif "education" in l:
            current = "Education"
        elif "skill" in l:
            current = "Skills"
        elif "achievement" in l:
            current = "Achievements"
        elif "language" in l:
            current = "Languages"
        elif "hobbies" in l or "interest" in l:
            current = "Hobbies"
        elif "phone" in l or "email" in l:
            current = "Contact"

        sections[current] += line + "\n"

    return sections

# ---------- SCORING ----------
def score_section(section, text):
    score = 80
    reasons = []
    suggestions = []
    t = text.lower()

    if section == "Experience":
        if not re.search(r"\d+", text):
            score -= 10
            reasons.append("No measurable achievements")
            suggestions.append("Add numbers (calls handled, % improvement)")

    elif section == "Education":
        if "%" not in text:
            score -= 10
            reasons.append("Marks not mentioned")
            suggestions.append("Add % or CGPA")

    elif section == "Skills":
        if len(text.split(",")) < 5:
            score -= 10
            reasons.append("Few skills listed")
            suggestions.append("Add more relevant skills")

    elif section == "Contact":
        if "@" not in text:
            score -= 10
            reasons.append("Email missing")
            suggestions.append("Add professional email")

    return max(score, 50), reasons, suggestions

# ---------- ATS SCORE ----------
def ats_score(text, job):
    resume_words = set(re.findall(r"\w+", text.lower()))
    job_words = set(re.findall(r"\w+", job.lower()))

    common = resume_words.intersection(job_words)

    if len(job_words) == 0:
        return 0

    return int((len(common) / len(job_words)) * 100)

# ---------- AI RESUME ----------
def generate_resume(text):
    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role":"system","content":"Create a professional resume with proper sections, bullets, and formatting."},
                {"role":"user","content":text}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return str(e)

# ---------- AI JOB MATCH ----------
def job_suggestions(text, job):
    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role":"system","content":"Analyze resume vs job role and suggest improvements."},
                {"role":"user","content":f"Resume:\n{text}\nJob:\n{job}"}
            ]
        )
        return res.choices[0].message.content
    except:
        return "Error in AI"

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)
    name = get_name(text)

    st.markdown(f'<div class="name">{name}</div>', unsafe_allow_html=True)

    sections = detect_sections(text)

    st.markdown("## 📊 Section Scores")

    cols = st.columns(4)
    scores = []

    for i, (sec, content) in enumerate(sections.items()):
        score, reasons, suggestions = score_section(sec, content)
        scores.append(score)

        with cols[i % 4]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{sec}**")
            st.progress(score)
            st.write(f"{score}/100")

            for r in reasons:
                st.write(f"❌ {r}")
            for s in suggestions:
                st.write(f"💡 {s}")

            st.markdown('</div>', unsafe_allow_html=True)

    overall = int(sum(scores)/len(scores))
    st.markdown("## 📈 Overall Score")
    st.progress(overall)
    st.write(f"{overall}/100")

    # ---------- ATS ----------
    if job_role:
        ats = ats_score(text, job_role)
        st.markdown("## 🎯 ATS Match Score")
        st.progress(ats)
        st.write(f"{ats}% match")

        st.markdown("## 🤖 Job Improvement Suggestions")
        st.write(job_suggestions(text, job_role))

    # ---------- AI RESUME ----------
    st.markdown("## ✨ Professional Resume")
    st.write(generate_resume(text))
