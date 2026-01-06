from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import os

from app.schemas.predict import PredictRequest
from app.ml.model import load_model
from app.db.session import get_db
from app.db.models import ModelInput, ModelOutput


# ============================================================
# ENV
# ============================================================

IS_TESTING = os.getenv("ENV") == "test"


# ============================================================
# CONSTANTES
# ============================================================

EXPECTED_FEATURES = [
    "age",
    "age_debut_carriere",
    "annee_experience_totale",
    "annees_dans_l_entreprise",
    "annees_dans_le_poste_actuel",
    "annees_depuis_la_derniere_promotion",
    "annee_derniere_promotion",
    "annes_sous_responsable_actuel",
    "genre",
    "statut_marital",
    "niveau_education",
    "domaine_etude",
    "departement",
    "poste",
    "niveau_hierarchique_poste",
    "frequence_deplacement",
    "revenu_mensuel",
    "augementation_salaire_precedente",
    "salaire_par_annee_exp",
    "heure_supplementaires",
    "distance_domicile_travail",
    "distance_x_deplacement",
    "impact_trajet_sur_satisfaction",
    "note_evaluation_actuelle",
    "note_evaluation_precedente",
    "evolution_note",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_environnement",
    "satisfaction_employee_equilibre_pro_perso",
    "satisfaction_employee_equipe",
    "satisfaction_moyenne",
    "score_satisfaction_global",
    "delta_satisfaction_equipe",
    "stagnation_poste",
    "stagnation_profonde",
    "taux_volatilite",
    "ratio_fidelite_entreprise",
    "ratio_poste_vs_anciennete",
    "anciennete_x_satisfaction",
    "nombre_experiences_precedentes",
    "nb_formations_suivies",
    "formations_par_annee",
    "nombre_participation_pee",
]


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="ML Model Deployment API",
    description="API exposing a machine learning model",
    version="1.0.0",
)

model = load_model()


# ============================================================
# ROUTES
# ============================================================

@app.get("/health")
def health():
    """
    Endpoint de vérification de santé de l'API.

    Returns
    -------
    dict
        Objet JSON simple indiquant le statut de l'API.
    """
    return {"status": "ok"}


@app.post("/predict")
def predict(
    request: PredictRequest,
    db: Session = Depends(get_db),
):
    """
    Endpoint de prédiction qui renvoie la prédiction et la probabilité.

    Parameters
    ----------
    request : PredictRequest
        Objet Pydantic contenant les features à prédire.
    db : Session, optional
        Session SQLAlchemy (injected par dépendance), par défaut Depends(get_db).

    Returns
    -------
    dict
        Dictionnaire contenant 'prediction' (0 ou 1) et 'probability' (float).

    Raises
    ------
    HTTPException
        400 en cas de features manquantes ou invalides, 500 en cas d'erreur interne.
    """
    try:
        # ----------------------------------------------------
        # 1. Vérification des features attendues
        # ----------------------------------------------------
        data = {}
        for feature in EXPECTED_FEATURES:
            if feature not in request.features:
                raise ValueError(f"Feature manquante : {feature}")
            data[feature] = request.features[feature]

        # ----------------------------------------------------
        # 2. Création DataFrame alignée avec le modèle
        # ----------------------------------------------------
        X = pd.DataFrame([data], columns=model.feature_names_in_)

        # ----------------------------------------------------
        # 3. Prédiction
        # ----------------------------------------------------
        proba = model.predict_proba(X)[0]
        probability = float(proba[1])
        prediction = int(probability >= 0.5)

        # ----------------------------------------------------
        # 4. Persistance DB (désactivée en tests / CI)
        # ----------------------------------------------------
        if not IS_TESTING:
            model_input = ModelInput(features=data)
            db.add(model_input)
            db.commit()
            db.refresh(model_input)

            model_output = ModelOutput(
                input_id=model_input.id,
                prediction=prediction,
                probability=probability,
            )
            db.add(model_output)
            db.commit()

        # ----------------------------------------------------
        # 5. Réponse API
        # ----------------------------------------------------
        return {
            "prediction": prediction,
            "probability": probability,
        }

    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        db.rollback()
        print("❌ Internal error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
