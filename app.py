import streamlit as st
import pdfplumber
import docx
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import re

st.set_page_config(layout="wide")
st.title("🚀 Professional Resume Analyzer & Builder")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# ---------------- TEXT EXTRACTION ----------------
def extract_text(file):
    text = ""

    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text

# ---------------- SMART SCORING ----------------
def calculate_score(text):
    score = 30
    issues = []

    word_count = len(text.split())

    if word_count > 200:
        score += 20
    else:
        issues.append("Resume is too short")

    if "experience" in text.lower():
        score += 15
    else:
        issues.append("Missing experience section")

    if "skills" in text.lower():
        score += 15
    else:
        issues.append("Missing skills section")

    if re.search(r"\d+", text):
        score += 10
    else:
        issues.append("Add measurable achievements (numbers)")

    if len(re.findall(r"\b(responsible|handled|worked)\b", text.lower())) > 5:
        score -= 10
        issues.append("Weak action words detected")

    return max(min(score, 95), 20), issues  # NEVER 100%

# ---------------- IMPROVEMENT ----------------
def improve_text(text):
    replacements = {
        "responsible for": "led and executed",
        "worked on": "developed and delivered",
        "handled": "managed efficiently"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text

# ---------------- HIGHLIGHT IMPORTANT LINES ----------------
def highlight_text(text):
    lines = text.split("\n")
    highlighted = []

    for line in lines:
        if re.search(r"\d+%|\d+", line):
            highlighted.append(f"<b>{line}</b>")
        else:
            highlighted.append(line)

    return "<br/>".join(highlighted)

# ---------------- PDF GENERATION ----------------
def create_pdf(content):
    doc = SimpleDocTemplate("resume.pdf", pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    for line in content.split("<br/>"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)

    with open("resume.pdf", "rb") as f:
        return f.read()

# ---------------- MAIN ----------------
if uploaded_file:
    text = extract_text(uploaded_file)

    if text:
        st.subheader("📊 Resume Score")
        score, issues = calculate_score(text)

        st.progress(score)
        st.write(f"Score: **{score}/100**")

        st.subheader("⚠️ Issues Found")
        for i in issues:
            st.write(f"• {i}")

        st.subheader("✨ Improved Resume")
        improved = improve_text(text)

        highlighted = highlight_text(improved)

        st.markdown(highlighted, unsafe_allow_html=True)

        # Generate PDF
        pdf = create_pdf(highlighted)

        st.download_button(
            "📥 Download Professional PDF Resume",
            pdf,
            file_name="professional_resume.pdf",
            mime="application/pdf"
        )
