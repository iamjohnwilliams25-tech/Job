import streamlit as st
import pdfplumber
import docx
from openai import OpenAI
import json

st.set_page_config(layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
st.markdown("""
<style>
body {background:#f4f6fb;}
.title {text-align:center;font-size:36px;font-weight:800;}
.card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 12px rgba(0,0,0,0.06);
    margin-bottom:10px;
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
Analyze this resume and return JSON ONLY.

Give scores (0-100) for:
Profile, Experience, Education, Skills, Achievements, Languages, Hobbies, Contact

Also give:
- reasons (why score is low)
- suggestions (how to improve)

Return STRICT JSON like:
{{
"profile": {{"score": 80, "reasons": ["..."], "suggestions": ["..."]}},
"experience": ...
}}

Resume:
{text}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3
        )

        return json.loads(res.choices[0].message.content)

    except Exception as e:
        st.error(e)
        return None

# ---------- ATS ----------
def ats_analysis(text, job):
    prompt = f"""
Compare this resume with job role.

Give:
- ATS match % (0-100)
- missing keywords
- improvement suggestions

Resume:
{text}

Job:
{job}
"""
    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content
    except:
        return "Error"

# ---------- MAIN ----------
if file:
    text = extract_text(file)

    st.write("Analyzing with AI...")

    data = analyze_resume(text)

    if data:

        st.markdown("## 📊 Section Scores")

        cols = st.columns(4)
        scores = []

        sections = list(data.keys())

        for i, sec in enumerate(sections):
            sec_data = data[sec]
            score = sec_data["score"]
            scores.append(score)

            with cols[i % 4]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write(f"**{sec.upper()}**")
                st.progress(score)
                st.write(f"{score}/100")

                for r in sec_data["reasons"]:
                    st.write(f"❌ {r}")

                for s in sec_data["suggestions"]:
                    st.write(f"💡 {s}")

                st.markdown('</div>', unsafe_allow_html=True)

        overall = int(sum(scores)/len(scores))

        st.markdown("## 📈 Overall Score")
        st.progress(overall)
        st.write(f"{overall}/100")

    # ---------- ATS ----------
    if job_role:
        st.markdown("## 🎯 ATS Analysis")
        st.write(ats_analysis(text, job_role))
