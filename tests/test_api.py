import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app

client = TestClient(app)


# ---------- FIXTURE FEATURES NON-CHURN ----------
@pytest.fixture
def features_non_churn():
    current_year = datetime.now(timezone.utc).year
    return {
        "age": 40,
        "age_debut_carriere": 22,
        "annee_experience_totale": 18,
        "annees_dans_l_entreprise": 10,
        "annees_dans_le_poste_actuel": 6,
        "annees_depuis_la_derniere_promotion": 1,
        "annee_derniere_promotion": current_year - 1,
        "annes_sous_responsable_actuel": 5,

        "genre": 1,
        "statut_marital": "Marié",
        "niveau_education": 4,
        "domaine_etude": "Informatique",

        "departement": "IT",
        "poste": "Lead Developer",
        "niveau_hierarchique_poste": 4,
        "frequence_deplacement": 0,

        "revenu_mensuel": 5000,
        "augementation_salaire_precedente": 10,
        "salaire_par_annee_exp": 60000,

        "heure_supplementaires": 0,
        "distance_domicile_travail": 5,
        "distance_x_deplacement": 5,
        "impact_trajet_sur_satisfaction": 0,

        "note_evaluation_actuelle": 5,
        "note_evaluation_precedente": 4,
        "evolution_note": 1,

        "satisfaction_employee_nature_travail": 5,
        "satisfaction_employee_environnement": 5,
        "satisfaction_employee_equilibre_pro_perso": 5,
        "satisfaction_employee_equipe": 5,
        "satisfaction_moyenne": 5,
        "score_satisfaction_global": 5,
        "delta_satisfaction_equipe": 0,

        "stagnation_poste": 0,
        "stagnation_profonde": 0,

        "taux_volatilite": 0.05,
        "ratio_fidelite_entreprise": 0.9,
        "ratio_poste_vs_anciennete": 0.6,
        "anciennete_x_satisfaction": 50,

        "nombre_experiences_precedentes": 1,
        "nb_formations_suivies": 10,
        "formations_par_annee": 2,
        "nombre_participation_pee": 5,
    }


# ---------- FIXTURE FEATURES CHURN (VALIDÉES ORM) ----------
@pytest.fixture
def features_churn():
    current_year = datetime.now(timezone.utc).year
    return {
        "age": 28,
        "age_debut_carriere": 22,
        "annee_experience_totale": 6,
        "annees_dans_l_entreprise": 1,
        "annees_dans_le_poste_actuel": 1,
        "annees_depuis_la_derniere_promotion": 1,
        "annee_derniere_promotion": current_year - 1,
        "annes_sous_responsable_actuel": 0,

        "genre": 0,
        "statut_marital": "Celibataire",
        "niveau_education": 2,
        "domaine_etude": "Autre",

        "departement": "Sales",
        "poste": "Commercial",
        "niveau_hierarchique_poste": 0,
        "frequence_deplacement": 2,

        "revenu_mensuel": 2200,
        "augementation_salaire_precedente": 0,
        "salaire_par_annee_exp": 26000,

        "heure_supplementaires": 1,
        "distance_domicile_travail": 50,
        "distance_x_deplacement": 100,
        "impact_trajet_sur_satisfaction": 5,

        "note_evaluation_actuelle": 2,
        "note_evaluation_precedente": 3,
        "evolution_note": -1,

        "satisfaction_employee_nature_travail": 1,
        "satisfaction_employee_environnement": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "satisfaction_employee_equipe": 1,
        "satisfaction_moyenne": 1,
        "score_satisfaction_global": 1,
        "delta_satisfaction_equipe": -2,

        "stagnation_poste": 1,
        "stagnation_profonde": 1,

        "taux_volatilite": 0.9,
        "ratio_fidelite_entreprise": 0.1,
        "ratio_poste_vs_anciennete": 0.9,
        "anciennete_x_satisfaction": 1,

        "nombre_experiences_precedentes": 4,
        "nb_formations_suivies": 0,
        "formations_par_annee": 0,
        "nombre_participation_pee": 0,
    }


# ---------- HEALTH ----------
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------- PREDICT NON-CHURN ----------
def test_predict_non_churn(features_non_churn):
    response = client.post("/predict", json={"features": features_non_churn})
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] == 0
    assert 0 <= data["probability"] <= 1


# ---------- PREDICT CHURN ----------
def test_predict_churn(features_churn):
    response = client.post("/predict", json={"features": features_churn})
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] == 1
    assert data["probability"] > 0.5


# ---------- VALIDATION ERROR (AGE) ----------
def test_predict_invalid_age(features_non_churn):
    payload = features_non_churn.copy()
    payload["age"] = 10  

    response = client.post("/predict", json={"features": payload})
    assert response.status_code == 400
    assert "age hors plage" in response.json()["detail"]
