import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template, jsonify, Blueprint
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

analysis_bp = Blueprint('analysis', __name__, template_folder="templates")

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def compute_similarity(resume_text, job_desc):
    if not resume_text:
        return 0, "Resume contains no relevant text."

    overall_embedding = model.encode([resume_text, job_desc])
    overall_score = cosine_similarity(
        [overall_embedding[0]], [overall_embedding[1]]
    )[0][0] * 100

    feedback_message = f"**Overall Match:** {round(overall_score, 2)}%\n"

    if overall_score > 80:
        feedback_message += "\n✅ Strong match! Minor tweaks needed."
    elif 50 <= overall_score <= 80:
        feedback_message += "\n⚡ Decent match. Consider refining your skills and project details."
    else:
        feedback_message += "\n❌ Low match. Update resume with relevant experience and skills."

    return round(overall_score, 2), feedback_message

@analysis_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "resume" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["resume"]
        job_desc = request.form.get("job_desc", "").strip()

        if file.filename == "" or not job_desc:
            return jsonify({"error": "Invalid input"}), 400

        filename = secure_filename(file.filename)
        if not filename.endswith(".pdf"):
            return jsonify({"error": "Only PDF resumes are supported."}), 400

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        resume_text = extract_text_from_pdf(filepath)

        if not resume_text:
            return jsonify({"error": "No extractable text from resume"}), 400

        score, feedback = compute_similarity(resume_text, job_desc)

        return render_template("index.html", score=score, feedback=feedback)

    return render_template("index.html", score=None, feedback=None)

# Main Flask app
app = Flask(__name__)
app.register_blueprint(analysis_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
