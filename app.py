import streamlit as st
import pdfplumber
import docx
from openai import OpenAI
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
st.markdown("""
<style>
body {background:#f4f6fb;}

.title {
    text-align:center;
    font-size:40px;
    font-weight:900;
}

.section-title {
    font-size:20px;
    font-weight:800;
    margin-bottom:10px;
}

.card {
    background: linear-gradient(135deg, #ffffff, #f1f5f9);
    padding:18px;
    border-radius:14px;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
    margin-bottom:15px;
}

.score-red {color:#dc2626; font-weight:800; font-size:22px;}
.score-green {color:#16a34a; font-weight:800; font-size:22px;}
.score-dark {color:#065f46; font-weight:900; font-size:24px;}

.big-score {
    text-align:center;
    font-size:52px;
    font-weight:900;
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

# ---------- COLOR ----------
def get_color(score):
    if score < 90:
        return "score-red"
    elif score == 100:
        return "score-dark"
    else:
        return "score-green"

# ---------- AI ----------
def analyze_resume(text):
    prompt = f"""
Return ONLY JSON:

{{
"profile": {{"score": 80, "reasons": ["..."], "suggestions": ["..."]}},
"experience": {{"score": 75, "reasons": ["..."], "suggestions": ["..."]}},
"education": {{"score": 70, "reasons": ["..."], "suggestions": ["..."]}},
"skills": {{"score": 85, "reasons": ["..."], "suggestions": ["..."]}},
"achievements": {{"score": 60, "reasons": ["..."], "suggestions": ["..."]}},
"languages": {{"score": 90, "reasons": ["..."], "suggestions": ["..."]}},
"hobbies": {{"score": 80, "reasons": ["..."], "suggestions": ["..."]}},
"contact": {{"score": 95, "reasons": ["..."], "suggestions": ["..."]}}
}}

Resume:
{text}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.2
        )

        content = res.choices[0].message.content.strip()

        if "```" in content:
            content = content.split("```")[1]

        return json.loads(content)

    except:
        return {
            k: {"score": 70, "reasons": ["Parsing issue"], "suggestions": ["Retry"]}
            for k in ["profile","experience","education","skills","achievements","languages","hobbies","contact"]
        }

# ---------- FINAL RESUME ----------
def generate_resume(text):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role":"user",
            "content":"Rewrite this resume professionally with clear sections and bullet points:\n"+text
        }]
    )
    return res.choices[0].message.content

# ---------- PDF (FIXED) ----------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = []
    for line in text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------- MAIN ----------
if file:
    text = extract_text(file)

    data = analyze_resume(text)

    scores = [data[s]["score"] for s in data]
    overall = int(sum(scores)/len(scores))

    # ---------- OVERALL ----------
    st.markdown("## 📊 Overall Score")
    color = get_color(overall)
    st.markdown(f'<div class="big-score {color}">{overall}/100</div>', unsafe_allow_html=True)
    st.progress(overall)

    # ---------- SECTIONS ----------
    st.markdown("## 📌 Section Analysis")

    cols = st.columns(2)

    for i, sec in enumerate(data):
        d = data[sec]
        color = get_color(d["score"])

        with cols[i % 2]:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(f'<div class="section-title">{sec.upper()}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{color}">{d["score"]}/100</div>', unsafe_allow_html=True)
            st.progress(d["score"])

            if d["reasons"]:
                st.write("❌ Why:")
                for r in d["reasons"]:
                    st.write(f"- {r}")

            if d["suggestions"]:
                st.write("💡 Fix:")
                for s in d["suggestions"]:
                    st.write(f"- {s}")

            st.markdown('</div>', unsafe_allow_html=True)

    # ---------- FINAL RESUME ----------
    st.markdown("## ✨ Final Professional Resume")

    final_resume = generate_resume(text)
    st.markdown(final_resume)

    # ---------- DOWNLOAD ----------
    pdf_buffer = create_pdf(final_resume)

    st.download_button(
        "📄 Download Resume",
        pdf_buffer,
        file_name="Professional_Resume.pdf",
        mime="application/pdf"
    )
