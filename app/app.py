import streamlit as st
import PyPDF2
import nltk
from collections import Counter
from docx import Document
import difflib  # For calculating similarity in plagiarism check
from dotenv import load_dotenv
load_dotenv()
import base64
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
from io import BytesIO
from fpdf import FPDF
import plotly.graph_objects as go

# Set Streamlit page config at the top
st.set_page_config(page_title="GLA ATS System", page_icon=":guardsman:")

nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Configure Google Generative AI
genai.configure(api_key=("AIzaSyBPDNB9oDlVpJlTdEkEnc7vWv_CsAZiVQ0"))

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def input_pdf_setup(pdf_file):
    return [extract_text_from_pdf(pdf_file)]

# Define the PDF class
class PDF(FPDF):
    def add_section(self, title, content):
        self.set_font('Arial', 'B', 14)
        self.cell(200, 10, title, ln=True)
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, content)
        self.ln(5)  # Add some space after each section

def generate_resume():
    """Function to generate PDF"""
    def generate_pdf(name, email, phone, skills, education, work_experience, projects, achievements, certifications, hobbies):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        text = c.beginText(50, 750)
    
        text.setFont("Helvetica", 12)
        text.textLine(f"Name: {name}")
        text.textLine(f"Email: {email}")
        text.textLine(f"Phone: {phone}")
        text.textLine("Skills:")
        text.textLines(skills)
        text.textLine("Education:")
        text.textLines(education)
        text.textLine("Work Experience:")
        text.textLines(work_experience)
        text.textLine("Projects:")
        text.textLines(projects)
        text.textLine("Achievements:")
        text.textLines(achievements)
        text.textLine("Certifications:")
        text.textLines(certifications)
        text.textLine("Hobbies:")
        text.textLines(hobbies)
    
        c.drawText(text)
        c.save()
    
        buffer.seek(0)
        return buffer
    
    # User inputs
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    skills = st.text_area("Skills")
    education = st.text_area("Education")
    work_experience = st.text_area("Work Experience")
    projects = st.text_area("Projects")
    achievements = st.text_area("Achievements")
    certifications = st.text_area("Certifications")
    hobbies = st.text_area("Hobbies")
    
    # Generate Resume
    if st.button("Generate Resume"):
        if not all([name, email, phone, skills, education, work_experience, projects, achievements, certifications, hobbies]):
            st.warning("Please fill in all fields before generating the resume.")
        else:
            pdf = generate_pdf(
                name,
                email,
                phone,
                skills,
                education,
                work_experience,
                projects,
                achievements,
                certifications,
                hobbies,
            )
    
            st.download_button(
                label="Download PDF",
                data=pdf,
                file_name="resume.pdf",
                mime="application/pdf"
            )

def get_gemini_response(resume_text, job_desc_text, prompt):
    """Fetches a response from Gemini API."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        input_text = f"Resume:\n{resume_text}\n\nJob Description:\n{job_desc_text}\n\nPrompt:\n{prompt}"
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        st.error(f"Error in Gemini API: {e}")
        return None

# Front Page
if st.session_state.get("page", "home") == "home":
    # Header with College Logo and title
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("path_to_college_logo.png", width=200)  # Add correct logo path
        st.markdown("<h1 style='text-align:center;'>GLA ATS SYSTEM</h1>", unsafe_allow_html=True)

    # Workflow description
    st.markdown("""
    ### Workflow:
    1. Upload your resume in PDF format.
    2. Choose from the analysis options:
       - **General Analysis** (AI-powered)
       - **Analysis with respect to Job Description**
       - **Grammatical Evaluation**
    3. Get insights and recommendations.
    """)

    # Upload resume option
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")
    if uploaded_file:
        st.session_state.page = "analysis"
        st.session_state.resume_file = uploaded_file

    # Sidebar option for Resume Creation
    st.sidebar.title("Options")
    option = st.sidebar.selectbox("Go to", ["Home", "Create Resume"])
    if option == "Create Resume":
        st.session_state.page = "resume_creation"
        generate_resume()

# Grammatical Evaluation
if st.session_state.get("page", "home") == "analysis":
    st.subheader("Select Analysis Type")
    analysis_type = st.selectbox("Choose Analysis Type", ["General Analysis", "Analysis with Job Description", "Grammatical Evaluation"])

    # On selecting Grammatical Evaluation
    if analysis_type == "Grammatical Evaluation":
        st.session_state.page = "grammatical_analysis"

# Grammatical Evaluation page
if st.session_state.get("page", "home") == "grammatical_analysis":
    st.subheader("Grammatical Evaluation")

    # Sidebar with options
    analysis_option = st.sidebar.selectbox("Choose an option", ["Repetitive Words", "Grammatical Errors"])

    if analysis_option == "Repetitive Words":
        text = extract_text_from_pdf(st.session_state.resume_file)
        doc = nltk.word_tokenize(text.lower())
        word_freq = Counter(word for word in doc if word.isalpha() and word not in stopwords.words('english'))
        st.write("Most common words:")
        for word, count in word_freq.most_common(10):
            st.write(f"{word}: {count} times")

    if analysis_option == "Grammatical Errors":
        # Placeholder for grammatical error analysis
        st.write("This feature will show grammatical errors detected in the resume.")
        # You can use language_tool or any other method to analyze grammatical errors

