from flask import Flask, request, jsonify, render_template, Blueprint
import PyPDF2
import io
from collections import defaultdict
from flask_cors import CORS

auth_bp = Blueprint('auth', __name__)
CORS(auth_bp)

# Mapping skills to job titles
JOB_MAPPINGS = {
    "python": "Software Developer",
    "javascript": "Frontend Developer",
    "java": "Software Engineer",
    "sql": "Data Analyst",
    "excel": "Data Analyst",
    "html": "Web Developer",
    "css": "Web Developer",
    "react": "React Developer",
    "node.js": "Backend Developer",
    "aws": "Cloud Engineer",
    "docker": "DevOps Engineer",
    "machine learning": "ML Engineer"
}

@auth_bp.route('/')
def home():
    return render_template('index.html')

def predict_jobs(skills):
    job_count = defaultdict(int)
    for skill in skills:
        job = JOB_MAPPINGS.get(skill)
        if job:
            job_count[job] += 1

    if job_count:
        # Sort jobs by number of skills matched
        sorted_jobs = sorted(job_count.items(), key=lambda x: x[1], reverse=True)
        return [job for job, count in sorted_jobs]
    
    return ["No Specific Match (General Position)"]

def calculate_proficiency(skills):
    proficiency = {}
    for skill in skills:
        # Simple method: assign a fixed proficiency for each found skill
        proficiency[skill] = 80  # Can vary this logic later
    return proficiency

def calculate_ats_score(proficiency_data):
    if not proficiency_data:
        return 0
    return int(sum(proficiency_data.values()) / len(proficiency_data))

@auth_bp.route('/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['resume']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400

        pdf_content = file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        resume_text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            resume_text += page_text or ""

        if resume_text.strip() == "":
            raise ValueError("Extracted text is empty. Maybe scanned PDF.")

        resume_text_lower = resume_text.lower()

        found_skills = set()
        for skill in JOB_MAPPINGS.keys():
            if skill in resume_text_lower:
                found_skills.add(skill)

        predicted_jobs = predict_jobs(found_skills)
        proficiency_data = calculate_proficiency(found_skills)
        ats_score = calculate_ats_score(proficiency_data)

        response = {
            "jobTitle": predicted_jobs,
            "skills": list(found_skills),
            "atsScore": ats_score,
            "proficiencyData": proficiency_data,
            "rawText": resume_text[:1000]  # limiting raw text preview
        }

        return jsonify(response)

    except Exception as e:
        print('Error analyzing resume:', str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    auth_bp.run(debug=True, port=5000)
