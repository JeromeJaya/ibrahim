from flask import Flask, render_template
from job_recommandetions.app import news_bp
from resume_analysis.app import auth_bp
from weitage_of_resume.app import analysis_bp

app = Flask(__name__)


# Register blueprints from each backend file
app.register_blueprint(news_bp, url_prefix='/news')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(analysis_bp, url_prefix='/analysis')

if __name__ == '__main__':
    app.run(debug=True)
