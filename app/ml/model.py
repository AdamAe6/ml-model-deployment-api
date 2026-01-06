import joblib
import os

MODEL_PATH = os.path.join('app', 'ml', 'models', 'model_p4.joblib')

def load_model():
    """
    Charger le modèle entraîné depuis le disque.

    Returns
    -------
    object
        Objet modèle chargé (par ex. un estimateur scikit-learn).

    Raises
    ------
    FileNotFoundError
        Si le fichier du modèle n'existe pas à l'emplacement attendu.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model P4 not found")
    return joblib.load(MODEL_PATH)
