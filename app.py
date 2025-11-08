import os
import json
import uuid
import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import nltk
from nltk.corpus import stopwords
import spacy
from pyresparser import ResumeParser
from sentence_transformers import SentenceTransformer, util
DATA_DIR = "/data"
STORE_FILE = os.path.join(DATA_DIR, "store.json")
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(STORE_FILE):
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump({"resumes": [], "matches": []}, f, indent=2)

app = Flask(__name__)
CORS(app)
STOP_WORDS = set(stopwords.words("english"))
# spaCy model (pre-downloaded in Dockerfile)
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("/root/.cache/huggingface/sentence-transformers/all-MiniLM-L6-v2")
def read_store():
    with open(STORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
def write_store(data):
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
def clean_and_extract_keywords(text: str):
    """Lowercase, tokenize, remove stopwords, lemmatize, deduplicate"""
    if not text:
        return []
    text = text.lower()
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.is_alpha and not token.is_stop and len(token.text) > 2:
            lemma = token.lemma_.strip()
            if lemma and lemma not in STOP_WORDS:
                keywords.append(lemma)
    seen = set()
    out = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out

# routes
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200
@app.route("/api/parse", methods=["POST"])
def parse_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filename = file.filename or f"resume_{uuid.uuid4().hex}"
    tmp_path = f"/tmp/{uuid.uuid4().hex}_{filename}"
    file.save(tmp_path)
    try:
        parsed = ResumeParser(tmp_path).get_extracted_data()
    except Exception as e:
        return jsonify({"error": f"Resume parsing failed: {str(e)}"}), 500
    parsed_clean = {
        "id": uuid.uuid4().hex,
        "filename": filename,
        "name": parsed.get("name"),
        "email": parsed.get("email"),
        "mobile_number": parsed.get("mobile_number"),
        "degree": parsed.get("degree"),
        "total_experience": parsed.get("total_experience"),
        "skills": parsed.get("skills") or [],
        "education": parsed.get("education"),
        "summary": parsed.get("summary"),
        "raw": parsed
    }
    store = read_store()
    store["resumes"].insert(0, {
        "id": parsed_clean["id"],
        "filename": parsed_clean["filename"],
        "name": parsed_clean["name"],
        "email": parsed_clean["email"],
        "skills": parsed_clean["skills"],
        "parsed_at": datetime.datetime.utcnow().isoformat() + "Z"
    })
    store["resumes"] = store["resumes"][:200]  # keep history trimmed
    write_store(store)
    return jsonify({"status": "ok", "parsed": parsed_clean}), 200
@app.route("/api/match", methods=["POST"])
def match_resume():
    payload = request.get_json() or {}
    resume_skills = payload.get("resumeSkills", [])  # list of strings
    title = payload.get("title", "")
    description = payload.get("description", "")

    jd_text = f"{title}\n{description}"
    required_keywords = clean_and_extract_keywords(jd_text)
    resume_text = " ".join([s.lower() for s in resume_skills]) if resume_skills else ""
    jd_for_embed = " ".join(required_keywords) if required_keywords else jd_text
    try:
        emb_jd = model.encode(jd_for_embed, convert_to_tensor=True)
        emb_resume = model.encode(resume_text, convert_to_tensor=True) if resume_text.strip() else None
        similarity = util.cos_sim(emb_resume, emb_jd).item() if emb_resume is not None else 0.0
        match_percent = round(float(similarity) * 100, 2)
    except Exception as e:
        return jsonify({"error": f"Embedding failed: {str(e)}"}), 500
    resume_norm = [s.lower() for s in resume_skills]
    matched = [k for k in required_keywords if k in resume_norm]
    missing = [k for k in required_keywords if k not in resume_norm]
    result = {
        "id": uuid.uuid4().hex,
        "title": title,
        "description": description,
        "required_keywords": required_keywords,
        "matched": matched,
        "missing": missing,
        "match_percent": match_percent,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    store = read_store()
    store["matches"].insert(0, result)
    store["matches"] = store["matches"][:200]
    write_store(store)
    return jsonify({"status": "ok", "result": result}), 200
@app.route("/api/history", methods=["GET"])
def history():
    store = read_store()
    return jsonify({"resumes": store.get("resumes", []), "matches": store.get("matches", [])}), 200
@app.route("/api/export", methods=["GET"])
def export_store():
    return send_file(STORE_FILE, as_attachment=True, download_name="store.json")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
