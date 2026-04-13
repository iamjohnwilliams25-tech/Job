import streamlit as st
import pdfplumber
import docx

st.set_page_config(layout="wide")
st.title("🚀 AI Resume Analyzer")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

# ---------------- EXTRACT TEXT ----------------
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

# ---------------- ANALYSIS ----------------
def analyze_resume(text):
    score = 50
    suggestions = []

    if len(text) > 500:
        score += 20
    else:
        suggestions.append("Add more content to your resume")

    if "experience" in text.lower():
        score += 10
    else:
        suggestions.append("Add experience section")

    if "skills" in text.lower():
        score += 10
    else:
        suggestions.append("Add skills section")

    if len(text.split()) > 150:
        score += 10
    else:
        suggestions.append("Increase word count for better ATS performance")

    return min(score, 100), suggestions

# ---------------- UI ----------------
if uploaded_file:

    text = extract_text(uploaded_file)

    if text:
        st.subheader("📄 Extracted Resume")
        st.text_area("Resume Content", text, height=200)

        score, suggestions = analyze_resume(text)

        st.subheader("📊 ATS Score")
        st.progress(score)
        st.write(f"Score: **{score}/100**")

        st.subheader("⚠️ Suggestions")
        for s in suggestions:
            st.write(f"• {s}")

        st.subheader("✨ Improved Version (Basic)")
        improved = text.replace("responsible for", "managed and executed")

        st.text_area("Improved Resume", improved, height=200)

        st.download_button(
            "📥 Download Improved Resume",
            improved,
            file_name="improved_resume.txt"
        )

    else:
        st.error("Could not extract text from file.")
