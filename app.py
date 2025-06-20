from flask import Flask, request, jsonify, render_template, Blueprint
from flask_cors import CORS
import fitz  # PyMuPDF
from flashtext import KeywordProcessor

news_bp = Blueprint('news', __name__)

CORS(news_bp, resources={r"/*": {"origins": "*"}})

# Dummy job database
jobs_db = [
    {"company": "Infosys", "location": "Chennai", "skills": ["python", "sql"], "lat": 13.0827, "lng": 80.2707},
    {"company": "TCS", "location": "Bangalore", "skills": ["java", "ml"], "lat": 12.9716, "lng": 77.5946},
    {"company": "Google", "location": "Hyderabad", "skills": ["python", "ml", "dl"], "lat": 17.3850, "lng": 78.4867}
]

# Skills list
skill_keywords = ["python", "sql", "java", "machine learning", "deep learning", "data analysis", "nlp", "ml", "dl"]
keyword_processor = KeywordProcessor()
for skill in skill_keywords:
    keyword_processor.add_keyword(skill)

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return " ".join(page.get_text() for page in doc)

def extract_skills(text):
    return list(set(keyword_processor.extract_keywords(text.lower())))

@news_bp.route('/')
def index():
    return render_template('index.html')

@news_bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        text = extract_text_from_pdf(file)
        user_skills = extract_skills(text)

        matched_jobs = []
        for job in jobs_db:
            matched = list(set(job['skills']) & set(user_skills))
            score = int((len(matched) / len(job['skills'])) * 100)
            if score > 0:
                matched_jobs.append({
                    "company": job['company'],
                    "location": job['location'],
                    "skills": job['skills'],
                    "match_score": score,
                    "lat": job['lat'],
                    "lng": job['lng']
                })

        return jsonify({"skills": user_skills, "matches": matched_jobs})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    news_bp.run(debug=True)
