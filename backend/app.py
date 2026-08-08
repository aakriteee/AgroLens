

import os
import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import database as db
from models.vgg16_svm import DiseaseDetector

app = Flask(__name__)
CORS(app)  # allow the mobile app (different origin) to call this API

# --- Config -----------------------------------------------------------
app.config["SECRET_KEY"] = os.environ.get("AGROLENS_SECRET_KEY", "dev-secret-change-me")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Startup: DB + ML model load once, not per request -----------------
db.init_db()

detector = None
try:
    detector = DiseaseDetector()
    print("VGG16 + SVM disease detector loaded successfully.")
except FileNotFoundError as e:
    # App can still start (e.g. for auth testing) even if the SVM
    # hasn't been trained yet -- /api/scan will just return an error.
    print(f"WARNING: {e}")


# --- Helpers ------------------------------------------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    """Decorator that protects a route: requires header
       Authorization: Bearer <token>"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated


# --- Auth routes ----------------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not full_name or not email or not password:
        return jsonify({"error": "full_name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if db.get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists"}), 409

    password_hash = generate_password_hash(password)
    user_id = db.create_user(full_name, email, password_hash)
    token = generate_token(user_id)

    return jsonify({
        "message": "Account created successfully",
        "token": token,
        "user": {"id": user_id, "full_name": full_name, "email": email},
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user["id"])
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {"id": user["id"], "full_name": user["full_name"], "email": user["email"]},
    }), 200


# --- Scan / Upload / Predict route -----------------------------------------

@app.route("/api/scan", methods=["POST"])
@token_required
def scan(current_user_id):
    """
    Accepts a multipart/form-data POST with a field named "image".
    Runs the VGG16 -> SVM pipeline and returns the predicted disease class.
    """
    if detector is None:
        return jsonify({
            "error": "Model not trained yet. Run models/train_model.py on the "
                     "server first."
        }), 503

    if "image" not in request.files:
        return jsonify({"error": "No image file provided (expected field 'image')"}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(image_file.filename):
        return jsonify({"error": "Only jpg, jpeg, png files are allowed"}), 400

    filename = secure_filename(
        f"user{current_user_id}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{image_file.filename}"
    )
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(save_path)

    try:
        label, confidence, all_probs = detector.predict(save_path)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 500

    recommendation = detector.get_recommendation(label)

    db.save_scan(current_user_id, filename, label, confidence, recommendation)

    return jsonify({
        "prediction": label,
        "confidence": round(confidence, 4),
        "all_class_probabilities": {k: round(v, 4) for k, v in all_probs.items()},
        "recommendation": recommendation,
        "image_url": f"/api/uploads/{filename}",
    }), 200


@app.route("/api/uploads/<filename>", methods=["GET"])
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# --- History route ----------------------------------------------------------

@app.route("/api/history", methods=["GET"])
@token_required
def history(current_user_id):
    scans = db.get_scans_for_user(current_user_id)
    result = [
        {
            "id": s["id"],
            "predicted_class": s["predicted_class"],
            "confidence": s["confidence"],
            "recommendation": s["recommendation"],
            "image_url": f"/api/uploads/{s['image_path']}",
            "created_at": s["created_at"],
        }
        for s in scans
    ]
    return jsonify({"history": result}), 200


# --- Health check -----------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": detector is not None,
    }), 200


if __name__ == "__main__":
    # host="0.0.0.0" so the phone (Expo Go app) on the same WiFi can reach it
    app.run(host="0.0.0.0", port=5000, debug=True)
