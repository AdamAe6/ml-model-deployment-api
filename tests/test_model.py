import pytest

from app.db.models import ModelInput
from datetime import datetime, timezone


# ---------- FIXTURE DE BASE VALIDE ----------
@pytest.fixture
def valid_features():
    current_year = datetime.now(timezone.utc).year
    return {
        "age": 35,
        "age_debut_carriere": 23,
        "annee_experience_totale": 12,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 3,
        "annees_depuis_la_derniere_promotion": 2,
        "annee_derniere_promotion": current_year - 2,
        "annes_sous_responsable_actuel": 2,

        "genre": 1,
        "statut_marital": "Celibataire",
        "niveau_education": 3,
        "domaine_etude": "Informatique",

        "departement": "IT",
        "poste": "Developpeur",
        "niveau_hierarchique_poste": 2,
        "frequence_deplacement": 1,

        "revenu_mensuel": 3000,
        "augementation_salaire_precedente": 5,
        "salaire_par_annee_exp": 36000,

        "heure_supplementaires": 1,
        "distance_domicile_travail": 15,
        "distance_x_deplacement": 30,
        "impact_trajet_sur_satisfaction": 2,

        "note_evaluation_actuelle": 4,
        "note_evaluation_precedente": 3,
        "evolution_note": 1,

        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_environnement": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_moyenne": 3,
        "score_satisfaction_global": 3,
        "delta_satisfaction_equipe": 0,

        "stagnation_poste": 0,
        "stagnation_profonde": 0,

        "taux_volatilite": 0.2,
        "ratio_fidelite_entreprise": 0.6,
        "ratio_poste_vs_anciennete": 0.5,
        "anciennete_x_satisfaction": 10,

        "nombre_experiences_precedentes": 2,
        "nb_formations_suivies": 4,
        "formations_par_annee": 1,
        "nombre_participation_pee": 1,
    }


# ---------- TEST OK ----------
def test_valid_features_pass(valid_features):
    obj = ModelInput(features=valid_features)
    assert obj.features["age"] == 35


# ---------- AGE ----------
def test_age_too_young(valid_features):
    valid_features["age"] = 15
    with pytest.raises(ValueError, match="age hors plage"):
        ModelInput(features=valid_features)


def test_age_start_after_age(valid_features):
    valid_features["age_debut_carriere"] = 40
    with pytest.raises(ValueError, match="age_debut_carriere"):
        ModelInput(features=valid_features)


# ---------- EXPERIENCE ----------
def test_negative_experience(valid_features):
    valid_features["annee_experience_totale"] = -1
    with pytest.raises(ValueError, match="experience"):
        ModelInput(features=valid_features)


def test_incoherent_age_experience(valid_features):
    valid_features["age_debut_carriere"] = 20
    valid_features["annee_experience_totale"] = 20
    valid_features["age"] = 35
    with pytest.raises(ValueError, match="incohérence âge"):
        ModelInput(features=valid_features)


# ---------- ANCIENNETE ----------
def test_poste_years_greater_than_anciennete(valid_features):
    valid_features["annees_dans_le_poste_actuel"] = 10
    valid_features["annees_dans_l_entreprise"] = 5
    with pytest.raises(ValueError, match="poste actuel"):
        ModelInput(features=valid_features)


def test_anciennete_greater_than_experience(valid_features):
    valid_features["annees_dans_l_entreprise"] = 15
    valid_features["annee_experience_totale"] = 10
    with pytest.raises(ValueError, match="ancienneté en entreprise"):
        ModelInput(features=valid_features)


# ---------- PROMOTION ----------
def test_negative_years_since_promo(valid_features):
    valid_features["annees_depuis_la_derniere_promotion"] = -1
    with pytest.raises(ValueError):
        ModelInput(features=valid_features)



# ---------- SALAIRE ----------
def test_negative_salary(valid_features):
    valid_features["revenu_mensuel"] = -100
    with pytest.raises(ValueError):
        ModelInput(features=valid_features)


def test_salary_vs_annual_salary_incoherent(valid_features):
    valid_features["revenu_mensuel"] = 2000
    valid_features["salaire_par_annee_exp"] = 100000
    with pytest.raises(ValueError, match="incohérence"):
        ModelInput(features=valid_features)


# ---------- DEPLACEMENT ----------
def test_invalid_frequence_deplacement(valid_features):
    valid_features["frequence_deplacement"] = 5
    with pytest.raises(ValueError):
        ModelInput(features=valid_features)


# ---------- EVALUATIONS ----------
def test_invalid_note(valid_features):
    valid_features["note_evaluation_actuelle"] = 6
    with pytest.raises(ValueError):
        ModelInput(features=valid_features)


def test_incoherent_evolution_note(valid_features):
    valid_features["note_evaluation_actuelle"] = 5
    valid_features["note_evaluation_precedente"] = 3
    valid_features["evolution_note"] = 1
    with pytest.raises(ValueError):
        ModelInput(features=valid_features)


# ---------- RATIOS ----------
def test_invalid_ratio(valid_features):
    valid_features["taux_volatilite"] = 1.5
    with pytest.raises(ValueError):
        ModelInput(features=valid_features)


# ---------- STAGNATION ----------
def test_invalid_stagnation_value(valid_features):
    valid_features["stagnation_poste"] = 2
    with pytest.raises(ValueError):
        ModelInput(features=valid_features)
