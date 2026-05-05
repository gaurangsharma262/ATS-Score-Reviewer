import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils import extract_text_from_pdf, extract_text_from_docx
from llm_scorer import get_ats_score
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Keep uploads simple - just read them in memory
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    # Ensure API Key is available
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return jsonify({"error": "Google API Key is missing. Please set it in the .env file."}), 400

    job_description = request.form.get('job_description', '')
    resume_input_method = request.form.get('input_method', 'paste')
    
    if not job_description.strip():
        return jsonify({"error": "Please provide a Job Description."}), 400

    resume_text = ""

    if resume_input_method == 'upload':
        if 'resume_file' not in request.files:
            return jsonify({"error": "No file uploaded."}), 400
        
        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({"error": "No file selected."}), 400

        # We can pass the file stream directly to our utils functions
        # But we need to check extension
        if file.filename.endswith('.pdf'):
            try:
                resume_text = extract_text_from_pdf(file)
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        elif file.filename.endswith('.docx'):
            try:
                resume_text = extract_text_from_docx(file)
            except Exception as e:
                return jsonify({"error": "Could not extract text from DOCX file."}), 400
        elif file.filename.endswith('.txt'):
            resume_text = file.read().decode('utf-8')
        else:
            return jsonify({"error": "Unsupported file format. Please upload PDF, DOCX, or TXT."}), 400

    else:
        # Paste Text method
        resume_text = request.form.get('resume_text', '')
        if not resume_text.strip():
            return jsonify({"error": "Please paste your resume text."}), 400

    try:
        # Get Score from LLM
        result = get_ats_score(resume_text, job_description)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
