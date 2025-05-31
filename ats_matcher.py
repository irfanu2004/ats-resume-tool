import streamlit as st
import re
import fitz  # PyMuPDF for PDFs
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# --- Razorpay payment link ---
razorpay_payment_link = "https://rzp.io/rzp/vu5XQA9"  # Your actual payment link here

# --- Page setup and intro message ---
st.set_page_config(
    page_title="ATS Resume Matcher - Improve Your Resume",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("📄 ATS Resume Matcher")
st.write("""
Welcome to the ATS Resume Matcher!  
Paste your resume or upload a PDF, and paste the job description to check your resume's keyword match score.  
Get instant feedback and download a detailed PDF report to optimize your resume for ATS.
""")

# --- Utility Functions ---

def clean_text(text):
    """Remove punctuation and make lowercase"""
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower().split()

def match_score(resume_text, job_desc_text):
    """Calculate match score and missing keywords"""
    resume_words = set(clean_text(resume_text))
    job_words = set(clean_text(job_desc_text))
    
    common_words = resume_words & job_words
    missing_words = job_words - resume_words
    
    if not job_words:
        return 0, []
    
    score = len(common_words) / len(job_words) * 100
    return round(score, 2), sorted(missing_words)

def extract_text_from_pdf(file):
    """Extract text from uploaded PDF file"""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def generate_pdf_report(score, missing_keywords):
    """Generate PDF report from score and missing keywords"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "ATS Resume Match Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Match Score: {score}%")

    if missing_keywords:
        c.drawString(50, height - 130, "Missing Keywords:")
        text_object = c.beginText(70, height - 150)
        for word in missing_keywords:
            text_object.textLine(f"- {word}")
        c.drawText(text_object)
    else:
        c.drawString(50, height - 130, "Great! Your resume includes all key job keywords.")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

# --- Streamlit UI ---

# Drag & drop file uploader (native supports drag and drop)
uploaded_file = st.file_uploader("📤 Upload Resume (PDF) — drag and drop supported", type=["pdf"])
resume_input = st.text_area("📄 Or Paste Resume Text", height=200)

job_desc_input = st.text_area("🧾 Job Description", height=200)

if st.button("🔍 Check Match"):
    if job_desc_input.strip() == "":
        st.warning("Please paste the job description.")
    else:
        if uploaded_file is not None:
            resume_text = extract_text_from_pdf(uploaded_file)
        elif resume_input.strip():
            resume_text = resume_input
        else:
            st.warning("Please upload or paste your resume.")
            st.stop()

        score, missing_keywords = match_score(resume_text, job_desc_input)

        st.success(f"✅ Match Score: {score}%")

        if missing_keywords:
            st.info("🧐 Missing Keywords:")
            st.write(", ".join(missing_keywords))
        else:
            st.balloons()
            st.success("🎉 Great! Your resume contains all key job keywords.")

        # Generate PDF report bytes
        pdf_bytes = generate_pdf_report(score, missing_keywords)

        # Payment & Download section
        st.markdown("---")
        st.markdown("### 💳 To Download Your Personalized Report")
        st.write("Pay ₹199 to download your ATS Match Report with improvement suggestions:")

        if st.button("🔐 Pay ₹199 and Unlock Payment Link"):
            st.markdown(
                f"[Click here to pay via Razorpay]({razorpay_payment_link})",
                unsafe_allow_html=True
            )
            st.info("After successful payment, please come back and check the box below to unlock the download.")

        # Confirm payment checkbox to unlock download button
        paid = st.checkbox("✅ I have completed the payment")

        if paid:
            st.download_button(
                label="📄 Download Report as PDF",
                data=pdf_bytes,
                file_name="match_report.pdf",
                mime="application/pdf"
            )
        else:
            st.info("Please complete the payment and check the box above to download your report.")
