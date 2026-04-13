import streamlit as st
import pdfplumber
import docx
import re
from openai import OpenAI

# ---------- PAGE ----------
st.set_page_config(layout="wide")

# ---------- DEBUG ----------
st.write("API KEY LOADED:", "OPENAI_API_KEY" in st.secrets)

# ---------- OPENAI ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
st.title("🚀 Resume Analyzer Pro (AI Powered)")
st.write("Upload resume and get smart improvements")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

# ---------- TEXT EXTRACTION ----------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    else:
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# ---------- AI FUNCTION ----------
def ai_improve_line(line):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Rewrite this resume sentence professionally using strong action verbs."},
                {"role": "user", "content": line}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"AI Error: {e}")  # 👈 shows error
        return None

# ---------- ANALYSIS ----------
def analyze(text):
    text_lower = text.lower()

    scores = {}
    suggestions = {}
    reasons = {}

    # EXPERIENCE ONLY (simple for now)
    score = 7
    reason = []
    sug = []

    if not re.search(r"\b(managed|led|developed)\b", text_lower):
        score -= 2
        reason.append("Weak action words used")
        sug.append("Use strong verbs like managed, led, developed")

    scores["Experience"] = score
    reasons["Experience"] = reason
    suggestions["Experience"] = sug

    return scores, suggestions, reasons

# ---------- MAIN ----------
if uploaded_file:
    text = extract_text(uploaded_file)

    scores, suggestions, reasons = analyze(text)

    st.subheader("📊 Score")
    for k, v in scores.items():
        st.write(f"{k}: {v}/10")

    st.subheader("💡 Feedback")
    for k in scores:
        if reasons[k]:
            st.write("❌ Why:")
            for r in reasons[k]:
                st.write(f"- {r}")

        if suggestions[k]:
            st.write("💡 Fix:")
            for s in suggestions[k]:
                st.code(s)

    # ---------- AI OUTPUT ----------
    st.subheader("✨ AI Improved Sentences")

    found = False

    for line in text.split("\n"):
        if len(line.strip()) > 20:
            improved = ai_improve_line(line)

            if improved:
                found = True
                st.write("**Original:**")
                st.code(line)

                st.write("**Improved:**")
                st.code(improved)

    if not found:
        st.warning("No AI output generated — check API or text")
