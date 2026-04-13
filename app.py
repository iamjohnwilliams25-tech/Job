import streamlit as st
from datetime import datetime

st.set_page_config(layout="centered")
st.title("🚀 AI Resume Builder & Analyzer")

st.caption(f"Build job-ready resume in seconds | {datetime.now().strftime('%Y-%m-%d')}")

# ---------------- INPUT SECTION ----------------
st.subheader("📄 Enter Your Details")

name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")

role = st.text_input("Target Job Role (e.g., Data Analyst)")

skills = st.text_area("Skills (comma separated)")
experience = st.text_area("Experience (write in bullet points)")
education = st.text_area("Education")

# ---------------- GENERATE BUTTON ----------------
if st.button("🚀 Generate Resume"):

    if not name or not skills:
        st.warning("Please fill at least Name and Skills")
    else:

        # ---------------- ATS SCORE ----------------
        score = 50

        if len(skills.split(",")) >= 5:
            score += 20
        if len(experience) > 50:
            score += 15
        if role:
            score += 15

        score = min(score, 100)

        # ---------------- SUGGESTIONS ----------------
        suggestions = []

        if len(skills.split(",")) < 5:
            suggestions.append("Add more relevant skills (at least 5+)")

        if len(experience) < 50:
            suggestions.append("Describe your experience in more detail with numbers/results")

        if not role:
            suggestions.append("Add target job role for better optimization")

        # ---------------- JOB MATCH TIPS ----------------
        job_tips = []
        if role:
            job_tips.append(f"Include keywords related to '{role}' in your resume")
            job_tips.append("Use action words like 'Developed', 'Managed', 'Improved'")
            job_tips.append("Add measurable achievements (e.g., increased sales by 20%)")

        # ---------------- RESUME OUTPUT ----------------
        resume_text = f"""
{name}
{email} | {phone}

🎯 Target Role:
{role}

💼 Skills:
{skills}

📌 Experience:
{experience}

🎓 Education:
{education}
"""

        # ---------------- DISPLAY ----------------
        st.success("✅ Resume Generated Successfully!")

        st.subheader("📊 ATS Score")
        st.progress(score)
        st.write(f"Score: **{score}/100**")

        st.subheader("📄 Your Resume")
        st.text(resume_text)

        st.subheader("💡 Improvement Suggestions")
        if suggestions:
            for s in suggestions:
                st.write(f"• {s}")
        else:
            st.write("✅ Your resume looks strong!")

        st.subheader("🎯 Job Optimization Tips")
        for tip in job_tips:
            st.write(f"• {tip}")

        # ---------------- DOWNLOAD ----------------
        st.download_button(
            label="📥 Download Resume",
            data=resume_text,
            file_name="resume.txt",
            mime="text/plain"
        )
