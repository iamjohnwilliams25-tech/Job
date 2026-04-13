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

.title {
    text-align:center;
    font-size:38px;
    font-weight:900;
}

.card {
    background:#ffffff;
    padding:12px;
    border-radius:10px;
    box-shadow:0 3px 8px rgba(0,0,0,0.06);
    margin-bottom:10px;
}

.section-title {
    font-size:16px;
    font-weight:800;
}

.small-text {
    font-size:13px;
    margin-bottom:4px;
}

.red {color:#dc2626; font-weight:700;}
.green {color:#16a34a; font-weight:800;}

.big-score {
    text-align:center;
    font-size:42px;
    font-weight:900;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Resume Analyzer AI PRO</div>', unsafe_allow_html=True)

file = st.file_uploader("Upload Resume", type=["pdf","docx"])
job_role = st.text_input("💼 Applying for positions (e.g. CSR, Sales Manager)")

analyze_btn = st.button("🔍 Analyze Resume")

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

# ---------- COLOR ----------
def get_color(score):
    return "green" if score == 100 else "red"

# ---------- AI ANALYSIS ----------
def analyze_resume(text, role):
    prompt = f"""
You are an expert ATS resume evaluator.

Evaluate this resume for the role: {role}

Return ONLY JSON.

{{
"profile": {{"score": 80, "reason": "...", "fix": "..."}},
"experience": {{"score": 75, "reason": "...", "fix": "..."}},
"education": {{"score": 70, "reason": "...", "fix": "..."}},
"skills": {{"score": 85, "reason": "...", "fix": "..."}},
"achievements": {{"score": 60, "reason": "...", "fix": "..."}},
"languages": {{"score": 90, "reason": "...", "fix": "..."}},
"hobbies": {{"score": 80, "reason": "...", "fix": "..."}},
"contact": {{"score": 95, "reason": "...", "fix": "..."}}
}}

Rules:
- Score based on relevance to job role
- Reason must be specific (NOT generic)
- Fix must be actionable

Resume:
{text}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3
        )

        content = res.choices[0].message.content.strip()

        if "```" in content:
            content = content.split("```")[1]

        return json.loads(content)

    except:
        return {
            k: {"score": 70, "reason": "Parsing issue", "fix": "Retry"}
            for k in ["profile","experience","education","skills","achievements","languages","hobbies","contact"]
        }

# ---------- FINAL RESUME ----------
def generate_resume(text, role):
    prompt = f"""
Rewrite this resume professionally for the role: {role}

Requirements:
- Strong ATS keywords for this role
- Clear sections
- Bullet points
- Impact-driven language
- Keep original data (no fake info)

Resume:
{text}
"""
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

# ---------- MAIN ----------
if file and job_role and analyze_btn:

    text = extract_text(file)

    data = analyze_resume(text, job_role)

    scores = [data[s]["score"] for s in data]
    overall = int(sum(scores)/len(scores))

    # ---------- OVERALL ----------
    st.markdown("## 📊 Overall Score")
    color = get_color(overall)
    st.markdown(f'<div class="big-score {color}">{overall}/100</div>', unsafe_allow_html=True)
    st.progress(overall)

    # ---------- SECTIONS ----------
    st.markdown("## 📌 Section Insights")

    cols = st.columns(2)

    for i, sec in enumerate(data):
        d = data[sec]
        color = get_color(d["score"])

        with cols[i % 2]:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(f'<div class="section-title">{sec.upper()} — <span class="{color}">{d["score"]}</span></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="small-text">❌ {d["reason"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="small-text">💡 {d["fix"]}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # ---------- FINAL RESUME ----------
    st.markdown("## ✨ Role-Based Improved Resume")

    final_resume = generate_resume(text, job_role)
    st.markdown(final_resume)
