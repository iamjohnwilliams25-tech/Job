import streamlit as st
import pdfplumber
import docx
from openai import OpenAI
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
st.markdown("""
<style>
body {background:#f4f6fb;}

.title {
    text-align:center;
    font-size:38px;
    font-weight:800;
}

.card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 12px rgba(0,0,0,0.06);
    height:260px;
    overflow:auto;
}

.score-big {
    text-align:center;
    font-size:40px;
    font-weight:800;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Resume Analyzer AI PRO</div>', unsafe_allow_html=True)

file = st.file_uploader("Upload Resume", type=["pdf","docx"])
job_role = st.text_input("🎯 Target Job Role")

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

# ---------- AI ANALYSIS ----------
def analyze_resume(text):
    prompt = f"""
Analyze resume and return JSON:

Sections: Profile, Experience, Education, Skills, Achievements, Languages, Hobbies, Contact

Each must include:
- score (0-100)
- reasons
- suggestions

Resume:
{text}
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )

    return json.loads(res.choices[0].message.content)

# ---------- FINAL RESUME ----------
def generate_final_resume(text):
    prompt = f"""
Rewrite resume in BEST PROFESSIONAL FORMAT:

- Big headings
- Bullet points
- Clean structure
- Corporate tone
- No fake data

Resume:
{text}
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}]
    )

    return res.choices[0].message.content

# ---------- PDF ----------
def create_pdf(text):
    file_path = "/mnt/data/resume.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    story = []
    for line in text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    return file_path

# ---------- MAIN ----------
if file:
    text = extract_text(file)

    data = analyze_resume(text)

    # ---------- OVERALL SCORE ----------
    scores = [data[s]["score"] for s in data]
    overall = int(sum(scores)/len(scores))

    st.markdown("## 📊 Overall Resume Score")
    st.markdown(f'<div class="score-big">{overall}/100</div>', unsafe_allow_html=True)
    st.progress(overall)

    # ---------- GRID ----------
    st.markdown("## 📌 Section Analysis")

    cols = st.columns(4)

    for i, sec in enumerate(data):
        d = data[sec]

        with cols[i % 4]:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.write(f"**{sec.upper()}**")
            st.progress(d["score"])
            st.write(f"{d['score']}/100")

            st.write("❌ Why:")
            for r in d["reasons"]:
                st.write(f"- {r}")

            st.write("💡 Fix:")
            for s in d["suggestions"]:
                st.write(f"- {s}")

            st.markdown('</div>', unsafe_allow_html=True)

    # ---------- FINAL RESUME ----------
    st.markdown("## ✨ Final Professional Resume")

    final_resume = generate_final_resume(text)

    st.markdown(final_resume)

    # ---------- DOWNLOAD ----------
    pdf_path = create_pdf(final_resume)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📄 Download Resume as PDF",
            data=f,
            file_name="Professional_Resume.pdf",
            mime="application/pdf"
        )
