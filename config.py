# config.py
import os

DB_DIR = "database"
MODEL_DIR = "models"

# Ensure directories exist (critical for fresh deploys like Render)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

AUTH_DB = os.path.join(DB_DIR, "auth.db")
FEEDBACK_DB = os.path.join(DB_DIR, "feedback.db")
TRUTH_DB = os.path.join(DB_DIR, "truthlens.db")

MODEL_FILE = os.path.join(MODEL_DIR, "finalized_model.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "vectorizer.pkl")
