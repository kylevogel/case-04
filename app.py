import hashlib
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from pydantic import ValidationError

from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line

app = Flask("survey-intake-api")

@app.get("/ping")
def ping():
    return jsonify({
        "message": "API is alive",
        "status": "ok",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })

@app.post("/v1/survey")
def submit_survey():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "invalid_json", "detail": "Body must be application/json"}), 400

    try:
        # Exercise 1: Add user_agent from headers
        payload['user_agent'] = request.headers.get('User-Agent')
        submission = SurveySubmission(**payload)
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422

    record = StoredSurveyRecord(
        **submission.dict(),
        received_at=datetime.now(timezone.utc),
        ip=request.headers.get("X-Forwarded-For", request.remote_addr or "")
    )

    # Exercise 3: Create submission_id
    current_hour_str = record.received_at.strftime('%Y%m%d%H')
    id_string_to_hash = submission.email + current_hour_str
    record.submission_id = hashlib.sha256(id_string_to_hash.encode('utf-8')).hexdigest()

    # Exercise 2: Hash PII before saving
    email_bytes = record.email.encode('utf-8')
    record.email = hashlib.sha256(email_bytes).hexdigest()
    
    age_bytes = str(record.age).encode('utf-8')
    record.age = hashlib.sha256(age_bytes).hexdigest()

    append_json_line(record.dict())
    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    app.run(port=5000, debug=True)
