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

.title {
    text-align:center;
    font-size:36px;
    font-weight:800;
}

.name {
    text-align:center;
    font-size:26px;
    font-weight:700;
    margin-bottom:20px;
}

.card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 12px rgba(0,0,0,0.06);
    margin-bottom:10px;
}

.red {color:#dc2626; font-weight:700;}
.green {color:#16a34a; font-weight:700;}
.amber {color:#d97706; font-weight:700;}
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

# ---------- NAME DETECTION (IMPROVED) ----------
def get_name(text):
    lines = text.split("\n")[:8]

    for line in lines:
        clean = line.strip()

        # Detect ALL CAPS name
        if clean.isupper() and 2 <= len(clean.split()) <= 4:
            return clean.title()

        # Detect normal name
        if 2 <= len(clean.split()) <= 4 and len(clean) > 5:
            return clean

    return "Candidate"

# ---------- SECTION DETECTION ----------
def detect_sections(text):
    sections = {
        "Profile": "",
        "Experience": "",
        "Education": "",
        "Skills": "",
        "Achievements": "",
        "Languages": "",
        "Hobbies": "",
        "Contact": ""
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
        elif "phone" in l or "email" in l or "address" in l:
            current = "Contact"

        sections[current] += line + "\n"

    return sections

# ---------- SCORING WITH REASONS ----------
def score_section(text):
    score = 60
    reasons = []
    suggestions = []

    if len(text.strip()) < 50:
        score -= 10
        reasons.append("Section content is too short")
        suggestions.append("Add more detailed information")

    if not re.search(r"\d+%|\d+", text):
        score -= 10
        reasons.append("No measurable results")
        suggestions.append("Add numbers like 20%, 30% growth")

    if not re.search(r"\b(managed|led|developed)\b", text.lower()):
        score -= 10
        reasons.append("Weak action verbs")
        suggestions.append("Use words like managed, led, developed")

    return max(score, 40), reasons, suggestions

def get_color(score):
    if score < 90:
        return "red"
    elif score == 100:
        return "green"
    else:
        return "amber"

# ---------- AI ----------
def generate_resume(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Rewrite this resume professionally:

- Extract candidate name clearly at top
- Use BIG section headings (## PROFILE, ## EXPERIENCE, etc.)
- Use bullet points
- Clean spacing
- Strong corporate tone
- Do NOT add fake data
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

    sections = detect_sections(text)

    st.markdown("## 📊 Section Score Dashboard")

    cols = st.columns(4)
    scores = []

    for i, (sec, content) in enumerate(sections.items()):
        score, reasons, suggestions = score_section(content)
        scores.append(score)
        color = get_color(score)

        with cols[i % 4]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{sec}**")
            st.markdown(f'<div class="{color}">{score}/100</div>', unsafe_allow_html=True)
            st.progress(score)

            if reasons:
                st.write("❌ Why:")
                for r in reasons:
                    st.write(f"- {r}")

            if suggestions:
                st.write("💡 Fix:")
                for s in suggestions:
                    st.code(s)

            st.markdown('</div>', unsafe_allow_html=True)

    overall = int(sum(scores) / len(scores))

    st.markdown("## 📈 Overall Score")
    color = get_color(overall)
    st.markdown(f'<div class="{color}">{overall}/100</div>', unsafe_allow_html=True)
    st.progress(overall)

    # ---------- AI OUTPUT ----------
    st.markdown("## ✨ Premium Resume Output")

    improved = generate_resume(text)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(improved)
    st.markdown('</div>', unsafe_allow_html=True)
