from fastapi import FastAPI, HTTPException
from app.schemas.predict import PredictRequest, PredictResponse
from app.ml.model import load_model
from app.db.session import SessionLocal
from app.db.models import ModelInput, ModelOutput
import pandas as pd
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

app = FastAPI(
    title="ML Model Deployment API",
    description="API exposing a machine learning model",
    version="1.0.0"
)

model = load_model()


@app.get("/health")
def health():
    return {"status": "ok"}




@app.post("/predict")
def predict(request: PredictRequest, db: Session = Depends(get_db)):
    db = SessionLocal()
    try:
        data = {}
        for feature in EXPECTED_FEATURES:
            if feature not in request.features:
                raise ValueError(f"Feature manquante : {feature}")
            data[feature] = request.features[feature]

        X = pd.DataFrame([data])
        try:

            if hasattr(model, 'feature_names_in_'):
                cols = list(model.feature_names_in_)
                X = X.reindex(columns=cols)
            else:

                try:
                    cols = model.booster_.feature_name()
                    X = X.reindex(columns=cols)
                except Exception:

                    X = X.reindex(columns=EXPECTED_FEATURES)

            missing = [c for c in X.columns if X[c].isnull().all()]
            if missing:
                raise ValueError(f"Features manquantes après alignement : {missing}")

        except ValueError:

            raise
        except Exception:
            
            X = pd.DataFrame([data], columns=EXPECTED_FEATURES)
        
        proba = model.predict_proba(X)
        prediction = int(proba[0].argmax())
        probability = float(proba[0][prediction])
        # Création input (déclenche validations ORM)
        model_input = ModelInput(features=data)
        db.add(model_input)
        db.commit()
        db.refresh(model_input)

        model_output = ModelOutput(
            input_id=model_input.id,
            prediction=prediction,
            probability=probability
        )

        db.add(model_output)
        db.commit()

        return {
            "prediction": prediction,
            "probability": probability
        }

    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:
        db.close()



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
    "nombre_participation_pee"
]
