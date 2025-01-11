import streamlit as st
import pdfplumber
import spacy
import language_tool_python
from collections import Counter
import base64
from pathlib import Path
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
import io

# Load SpaCy model for text processing
nlp = spacy.load("en_core_web_sm")

# Initialize LanguageTool for grammar checking
tool = language_tool_python.LanguageTool('en-US')

# Configure Gemini API
def configure_gemini():

    genai.configure(api_key="AIzaSyDq1wgsd_UjFTez-e8ptUDQlGBSAE-lmuM")
    return genai.GenerativeModel('gemini-pro')

def load_css():
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 20px;
        }
        .workflow-section {
            margin: 20px 0;
            padding: 20px;
            background-color: #f0f2f6;
            border-radius: 10px;
        }
        .analysis-box {
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def analyze_resume_with_gemini(model, resume_text, analysis_type="general"):
    if analysis_type == "general":
        prompt = f"""
        Analyze the following resume and provide detailed feedback on:
        1. Overall structure and formatting
        2. Key skills and qualifications
        3. Experience highlights
        4. Areas for improvement
        5. Professional summary recommendations

        Resume:
        {resume_text}
        """
    else:
        prompt = f"""
        Analyze the following resume text for grammatical issues and provide:
        1. List of grammatical errors
        2. Suggestions for improvement
        3. Overall writing style feedback
        4. Formality and tone assessment

        Resume:
        {resume_text}
        """

    response = model.generate_content(prompt)
    return response.text

def analyze_resume_with_job_description(model, resume_text, job_description):
    prompt = f"""
    Compare the following resume with the job description and provide:
    1. Match percentage for required skills
    2. Missing key requirements
    3. Relevant experience alignment
    4. Suggested modifications
    5. Keywords to add

    Resume:
    {resume_text}

    Job Description:
    {job_description}
    """

    response = model.generate_content(prompt)
    return response.text

def analyze_repetitive_words(text):
    doc = nlp(text)
    words = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
    word_freq = Counter(words)
    return word_freq.most_common(10)

def create_download_link(content, filename):
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download Resume</a>'

def main():
    st.set_page_config(page_title="GLA ATS System", layout="wide")
    load_css()

    # Initialize Gemini model
    try:
        model = configure_gemini()
    except Exception as e:
        st.error("Error initializing Gemini API. Please check your API key.")
        return

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Resume Creation"])

    if page == "Home":
        # Header with logo
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("/content/GLA_University_logo.png", width=200)  # Replace with actual logo path
            st.markdown("<h1 class='main-header'>GLA ATS SYSTEM</h1>", unsafe_allow_html=True)

        # Workflow section
        st.markdown("<div class='workflow-section'>", unsafe_allow_html=True)
        st.markdown("""
        ### Workflow
        1. Upload your resume in PDF format
        2. Choose from three analysis options:
           - General Analysis (AI-powered)
           - Analysis with respect to Job Description
           - Grammatical Evaluation
        3. Get detailed insights and recommendations
        """)
        st.markdown("</div>", unsafe_allow_html=True)

        # File upload section
        st.header("Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file is not None:
            text = extract_text_from_pdf(uploaded_file)

            analysis_type = st.selectbox(
                "Choose Analysis Type",
                ["General Analysis", "Analysis respect to Job description", "Grammatical Evaluation"]
            )

            if analysis_type == "Grammatical Evaluation":
                st.sidebar.header("Grammar Analysis Options")

                if st.sidebar.button("AI Grammar Analysis"):
                    with st.spinner("Analyzing grammar with AI..."):
                        grammar_analysis = analyze_resume_with_gemini(model, text, "grammar")
                        st.markdown(f"<div class='analysis-box'>{grammar_analysis}</div>", unsafe_allow_html=True)

                if st.sidebar.button("Repetitive Words"):
                    repetitive_words = analyze_repetitive_words(text)
                    st.subheader("Most Common Words")
                    for word, count in repetitive_words:
                        st.write(f"{word}: {count} times")

            elif analysis_type == "General Analysis":
                if st.button("Analyze Resume"):
                    with st.spinner("Analyzing resume with AI..."):
                        analysis = analyze_resume_with_gemini(model, text)
                        st.markdown(f"<div class='analysis-box'>{analysis}</div>", unsafe_allow_html=True)

            elif analysis_type == "Analysis respect to Job description":
                st.subheader("Job Description Analysis")
                job_desc = st.text_area("Paste the Job Description")
                if job_desc and st.button("Compare with Job Description"):
                    with st.spinner("Analyzing resume against job description..."):
                        comparison = analyze_resume_with_job_description(model, text, job_desc)
                        st.markdown(f"<div class='analysis-box'>{comparison}</div>", unsafe_allow_html=True)

    else:  # Resume Creation page
        st.header("Resume Creation")

        # Personal Information
        st.subheader("Personal Information")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")

        # Education
        st.subheader("Education")
        degree = st.text_input("Degree")
        university = st.text_input("University")
        graduation_year = st.text_input("Graduation Year")

        # Experience
        st.subheader("Experience")
        company = st.text_input("Company Name")
        position = st.text_input("Position")
        duration = st.text_input("Duration")
        responsibilities = st.text_area("Responsibilities")

        # Skills
        st.subheader("Skills")
        skills = st.text_area("List your skills (comma-separated)")

        if st.button("Generate Resume"):
            resume_content = f"""
            {name}
            {email} | {phone}

            EDUCATION
            {degree}
            {university}, {graduation_year}

            EXPERIENCE
            {company}
            {position} ({duration})
            {responsibilities}

            SKILLS
            {skills}
            """

            st.markdown(create_download_link(resume_content, "resume.txt"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
