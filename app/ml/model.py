import joblib
import os

MODEL_PATH = os.path.join('app', 'ml', 'models', 'model_p4.joblib')

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model P4 not found")
    return joblib.load(MODEL_PATH)
