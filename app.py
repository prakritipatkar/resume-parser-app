import os
import requests
from flask import Flask, request, render_template, jsonify
from PyPDF2 import PdfReader
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import logging
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Setup Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store resume text and LinkedIn content for Q&A
resume_text_store = {}
linkedin_content_store = {}

# ========== Extract text ==========

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join([page.extract_text() or '' for page in reader.pages])
        logger.info(f"Extracted text length: {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return ""

def split_text(text, max_chars=5000):
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        chunks = splitter.create_documents([text])
        result = "\n".join([chunk.page_content for chunk in chunks[:3]])
        logger.info(f"Split text length: {len(result)} characters")
        return result
    except Exception as e:
        logger.error(f"Error splitting text: {str(e)}")
        return text[:max_chars]

# ========== Fetch LinkedIn content ==========

def fetch_linkedin_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract main profile sections (name, headline, about, experience, education)
        profile_content = ""
        # Name
        name = soup.find('h1', class_='text-heading-xlarge')
        if name:
            profile_content += f"Name: {name.get_text(strip=True)}\n"
        # Headline
        headline = soup.find('div', class_='text-body-medium')
        if headline:
            profile_content += f"Headline: {headline.get_text(strip=True)}\n"
        # About section
        about = soup.find('div', class_='pv-about-section')
        if about:
            profile_content += f"About: {about.get_text(strip=True)}\n"
        # Experience
        experience = soup.find_all('div', class_='pv-entity__summary-info')
        if experience:
            profile_content += "Experience:\n"
            for exp in experience:
                title = exp.find('h3')
                company = exp.find('p', class_='pv-entity__secondary-title')
                if title and company:
                    profile_content += f"- {title.get_text(strip=True)} at {company.get_text(strip=True)}\n"
        # Education
        education = soup.find_all('div', class_='pv-education-entity')
        if education:
            profile_content += "Education:\n"
            for edu in education:
                school = edu.find('h3')
                degree = edu.find('p', class_='pv-entity__degree-name')
                if school and degree:
                    profile_content += f"- {degree.get_text(strip=True)} from {school.get_text(strip=True)}\n"
        logger.info(f"Fetched LinkedIn content from {url}, length: {len(profile_content)} characters")
        return profile_content[:10000]  # Limit content to avoid overwhelming Gemini
    except Exception as e:
        logger.error(f"Error fetching LinkedIn content from {url}: {str(e)}")
        return ""

# ========== Gemini query ==========

def ask_gemini(resume_text, question, linkedin_content=None):
    prompt = f"""
You are a resume analyzer AI. Extract only the answer from the provided content. Prioritize LinkedIn content if available for relevant fields.

Resume:
\"\"\"{resume_text}\"\"\"
"""
    if linkedin_content:
        prompt += f"""
LinkedIn Profile Content:
\"\"\"{linkedin_content}\"\"\"
"""
    prompt += f"""
Question:
{question}

Return the most accurate answer or say 'Not Found' if unavailable.
"""
    try:
        response = gemini_model.generate_content(prompt)
        answer = response.text.strip() if response.text else "Not Found"
        logger.info(f"Gemini answered for '{question}': {answer}")
        return answer
    except Exception as e:
        logger.error(f"Gemini Error for question '{question}': {str(e)}")
        return f"Error: {str(e)}"

# ========== Routes ==========

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        return jsonify({"error": "Template not found"}), 500

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        logger.error("No file uploaded in request")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.pdf'):
        logger.error(f"Invalid file format: {file.filename}")
        return jsonify({"error": "Only PDF files are allowed"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(filepath)
        logger.info(f"Saved file to: {filepath}")
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {str(e)}")
        return jsonify({"error": "Failed to save file"}), 500

    # Extract and split text
    raw_text = extract_text_from_pdf(filepath)
    if not raw_text:
        logger.error("No text extracted from PDF")
        return jsonify({"error": "Failed to extract text from PDF"}), 500

    resume_text = split_text(raw_text)
    resume_text_store['current'] = resume_text  # Store for Q&A

    # Gemini-powered field questions
    fields = {
        "Name": "What is the candidate's full name?",
        "Email": "What is the candidate's email address?",
        "Phone": "What is the candidate's phone number?",
        "Education": "List the candidate's educational qualifications.",
        "Address": "What is the candidate's address?",
        "LinkedIn": "What is the LinkedIn profile link?",
        "CurrentJob": "What is the candidate's current job title and company?",
        "Experience": "How many years of experience does the candidate have?",
        "Skills": "List the candidate's technical or soft skills.",
        "Projects": "List the candidate's notable projects."
    }

    results = {}
    linkedin_content = None
    linkedin_url = None

    # First pass: Get LinkedIn URL if available
    for key, question in fields.items():
        if key == "LinkedIn":
            linkedin_url = ask_gemini(resume_text, question)
            results[key] = linkedin_url
            if linkedin_url and linkedin_url != "Not Found" and re.match(r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$', linkedin_url):
                linkedin_content = fetch_linkedin_content(linkedin_url)
                linkedin_content_store['current'] = linkedin_content  # Store for Q&A
            break

    # Second pass: Process all fields, using LinkedIn content if available
    for key, question in fields.items():
        if key != "LinkedIn":  # Skip LinkedIn since it's already processed
            logger.info(f"Asking Gemini: {question}")
            answer = ask_gemini(resume_text, question, linkedin_content)
            results[key] = answer

    logger.info(f"Returning results: {results}")
    return jsonify(results)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    if not question:
        logger.error("No question provided")
        return jsonify({"error": "No question provided"}), 400

    resume_text = resume_text_store.get('current', '')
    linkedin_content = linkedin_content_store.get('current', '')

    if not resume_text:
        logger.error("No resume text available for Q&A")
        return jsonify({"error": "No resume data available"}), 400

    logger.info(f"Processing Q&A: {question}")
    answer = ask_gemini(resume_text, question, linkedin_content)
    return jsonify({"answer": answer})

# ========== Run App ==========

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000) 