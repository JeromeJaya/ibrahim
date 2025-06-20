from flask import Flask, request, jsonify
import PyPDF2
import io
import spacy
from collections import defaultdict
import numpy as np
from flask_cors import CORS

app = Flask(_name_)
CORS(app)  # Enable CORS for all routes

# Load English language model for spaCy
nlp = spacy.load("en_core_web_sm")

# Define job mappings and skill sets
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

# Skill categories with related terms
SKILL_CATEGORIES = {
    "programming": ["python", "java", "javascript", "c++", "c#", "ruby", "go", "rust"],
    "web": ["html", "css", "javascript", "react", "angular", "vue", "node.js"],
    "data": ["sql", "excel", "pandas", "numpy", "spark", "hadoop"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
    "ml": ["machine learning", "tensorflow", "pytorch", "scikit-learn"]
}

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported"}), 400
    
    try:
        # Read PDF content
        pdf_content = file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        resume_text = ""
        
        for page in pdf_reader.pages:
            resume_text += page.extract_text() or ""
        
        # Process text with spaCy
        doc = nlp(resume_text.lower())
        
        # Extract skills and predict job title
        found_skills = set()
        predicted_job = "General Position"
        job_counts = defaultdict(int)
        
        # Check for skills in the text
        for skill, job in JOB_MAPPINGS.items():
            if skill in resume_text.lower():
                found_skills.add(skill)
                job_counts[job] += 1
        
        # Predict job title based on most mentioned job category
        if job_counts:
            predicted_job = max(job_counts.items(), key=lambda x: x[1])[0]
        
        # Categorize skills
        categorized_skills = defaultdict(list)
        for skill in found_skills:
            for category, skills in SKILL_CATEGORIES.items():
                if skill in skills:
                    categorized_skills[category].append(skill)
        
        # Estimate proficiency (simple heuristic)
        proficiency = {}
        for skill in found_skills:
            # Basic heuristic: more mentions = higher proficiency
            mentions = resume_text.lower().count(skill)
            proficiency[skill] = min(60 + (mentions * 10), 100)
        
        # Generate response
        response = {
            "jobTitle": predicted_job,
            "skills": list(found_skills),
            "categorizedSkills": dict(categorized_skills),
            "proficiency": proficiency,
            "rawText": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if _name_ == '_main_':
    app.run(debug=True, port=5000)