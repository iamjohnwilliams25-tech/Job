import streamlit as st
import pdfplumber
import docx
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

st.set_page_config(layout="wide")
st.title("🚀 Smart Resume Analyzer (Professional Version)")

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

# ---------------- SCORE ----------------
def calculate_score(text):
    score = 40
    issues = []

    if len(text.split()) > 200:
        score += 15
    else:
        issues.append("Resume is too short")

    if re.search(r"\d+", text):
        score += 10
    else:
        issues.append("Add measurable achievements (numbers)")

    weak_words = re.findall(r"\b(responsible|handled|worked|helped)\b", text.lower())
    if len(weak_words) > 5:
        score -= 10
        issues.append("Too many weak action words")

    if "experience" not in text.lower():
        issues.append("Missing experience section")

    return max(min(score, 85), 30), issues  # realistic cap

# ---------------- LINE IMPROVEMENT ----------------
def suggest_improvement(line):
    replacements = {
        "responsible for": "led and executed",
        "handled": "managed efficiently",
        "worked on": "developed and delivered",
        "helped": "contributed to"
    }

    improved = line
    for k, v in replacements.items():
        improved = re.sub(k, v, improved, flags=re.IGNORECASE)

    return improved

# ---------------- HIGHLIGHT ----------------
def highlight_line(line):
    if re.search(r"\d+|\b(managed|led|developed|improved)\b", line.lower()):
        return f"<b>{line}</b>"
    return line

# ---------------- PDF ----------------
def create_pdf(lines):
    doc = SimpleDocTemplate("resume.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    for line in lines:
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 8))

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

        st.subheader("🧠 Smart Improvements (Choose what to fix)")

        lines = text.split("\n")
        improved_lines = []

        for i, line in enumerate(lines):
            if len(line.strip()) > 20:

                suggestion = suggest_improvement(line)

                if suggestion != line:
                    st.write(f"**Original:** {line}")
                    st.write(f"👉 Suggested: {suggestion}")

                    apply_fix = st.checkbox(f"Apply fix for line {i}")

                    if apply_fix:
                        improved_lines.append(suggestion)
                    else:
                        improved_lines.append(line)
                else:
                    improved_lines.append(line)
            else:
                improved_lines.append(line)

        st.subheader("✨ Final Resume Preview")

        highlighted = [highlight_line(l) for l in improved_lines]

        st.markdown("<br>".join(highlighted), unsafe_allow_html=True)

        pdf = create_pdf(highlighted)

        st.download_button(
            "📥 Download Professional Resume PDF",
            pdf,
            file_name="final_resume.pdf",
            mime="application/pdf"
        )

    else:
        st.error("Could not extract text from file.")
