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
.subtitle {text-align:center;color:#6b7280;margin-bottom:20px;}
.card {
    background:white;
    padding:18px;
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
st.markdown('<div class="subtitle">AI-powered professional resume builder</div>', unsafe_allow_html=True)

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

# ---------- SMART SECTION DETECTION ----------
def detect_sections(text):
    sections = {
        "Profile": "",
        "Education": "",
        "Experience": "",
        "Skills": "",
        "Languages": "",
        "Hobbies": "",
        "Contact": ""
    }

    current = "Profile"

    for line in text.split("\n"):
        l = line.lower()

        if any(k in l for k in ["education", "academic"]):
            current = "Education"
        elif any(k in l for k in ["experience", "work"]):
            current = "Experience"
        elif "skill" in l:
            current = "Skills"
        elif any(k in l for k in ["language"]):
            current = "Languages"
        elif any(k in l for k in ["hobbies", "interest"]):
            current = "Hobbies"
        elif any(k in l for k in ["phone", "email", "address"]):
            current = "Contact"

        sections[current] += line + "\n"

    return sections

# ---------- AI FULL RESUME ----------
def generate_professional_resume(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an expert resume writer.

Rewrite the entire resume professionally with:
- Clear sections (Profile, Experience, Education, Skills, Languages, Hobbies, Contact)
- Bold section headings
- Bullet points for responsibilities
- Strong action verbs
- Clean formatting
- Keep content realistic (do NOT add fake experience)
- Make it look like a premium corporate resume
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.5
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"

# ---------- SCORING ----------
def score_resume(text):
    score = 60

    if re.search(r"\d+%|\d+", text):
        score += 10
    if re.search(r"\b(managed|led|developed)\b", text.lower()):
        score += 10
    if "skills" in text.lower():
        score += 10
    if "experience" in text.lower():
        score += 10

    return min(score, 95)

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)

    # SCORE
    score = score_resume(text)

    st.markdown("## 📊 Resume Score")
    st.progress(score)
    st.success(f"{score}/100")

    # ORIGINAL
    st.markdown("## 📄 Original Resume")
    st.code(text)

    # AI OUTPUT
    st.markdown("## ✨ Professional Resume (AI Generated)")

    improved = generate_professional_resume(text)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(improved)
    st.markdown('</div>', unsafe_allow_html=True)
