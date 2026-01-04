from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship, validates
from datetime import datetime, timezone

Base = declarative_base()

class ModelInput(Base):
    __tablename__ = "model_inputs"

    id = Column(Integer, primary_key=True)

    # Données envoyées au modèle
    features = Column(JSONB, nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relation ORM
    outputs = relationship(
        "ModelOutput",
        back_populates="input",
        cascade="all, delete-orphan"
    )

    # -------- RÈGLES ORM PYTHON (VALIDATIONS) --------
    @validates("features")
    def validate_features(self, key, value):

        # --- AGE ---
        age = value.get("age")
        if age is None or age < 16 or age > 70:
            raise ValueError("age hors plage réaliste (16–70)")

        age_start = value.get("age_debut_carriere")
        if age_start is not None and age_start >= age:
            raise ValueError("age_debut_carriere doit être inférieur à age")

        # --- EXPERIENCE ---
        exp = value.get("annee_experience_totale")
        if exp is not None and exp < 0:
            raise ValueError("annee_experience_totale ne peut pas être négatif")

        if age_start is not None and exp is not None:
            if age_start + exp > age:
                raise ValueError("incohérence âge / expérience")

        # --- ANCIENNETE ---
        anciennete = value.get("annees_dans_l_entreprise")
        if anciennete is not None and anciennete < 0:
            raise ValueError("ancienneté négative interdite")

        poste_years = value.get("annees_dans_le_poste_actuel")
        if poste_years is not None and anciennete is not None:
            if poste_years > anciennete:
                raise ValueError("poste actuel > ancienneté entreprise")

        # --- Vérification cohérence ancienneté vs expérience totale ---
        if exp is not None and anciennete is not None:
            if anciennete > exp:
                raise ValueError("ancienneté en entreprise ne peut pas dépasser l'expérience totale")

        # --- PROMOTION ---
        annees_depuis_promo = value.get("annees_depuis_la_derniere_promotion")
        annee_derniere_promo = value.get("annee_derniere_promotion")
        current_year = datetime.now(timezone.utc).year

        if annees_depuis_promo is not None:
            if annees_depuis_promo < 0:
                raise ValueError("annees_depuis_la_derniere_promotion ne peut pas être négatif")
            if anciennete is not None and annees_depuis_promo > anciennete:
                raise ValueError("annees_depuis_la_derniere_promotion ne peut pas être supérieure à l'ancienneté")

        if annee_derniere_promo is not None:
            if not (1900 <= annee_derniere_promo <= current_year):
                raise ValueError("annee_derniere_promotion invalide")
            if annees_depuis_promo is not None:
                # cohérence simple: nombre d'années depuis promotion devrait correspondre
                if current_year - annee_derniere_promo != int(annees_depuis_promo):
                    raise ValueError("incohérence entre annee_derniere_promotion et annees_depuis_la_derniere_promotion")

        # --- RESPONSABILITE ---
        sous_resp = value.get("annes_sous_responsable_actuel")
        if sous_resp is not None:
            if sous_resp < 0:
                raise ValueError("annes_sous_responsable_actuel ne peut pas être négatif")
            if poste_years is not None and sous_resp > poste_years:
                raise ValueError("annes_sous_responsable_actuel ne peut pas dépasser les années dans le poste actuel")

        # --- DEMOGRAPHIQUE ---
        genre = value.get("genre")
        if genre is not None and genre not in [0, 1, 2]:
            raise ValueError("genre doit être 0, 1 ou 2")

        statut = value.get("statut_marital")
        if statut is not None:
            if not isinstance(statut, str) or not statut:
                raise ValueError("statut_marital doit être une chaîne non vide")
            allowed_statuts = {"Celibataire", "Marie", "Marié", "Divorce", "Divorcé", "Veuf", "Separation", "Séparé"}
            # on accepte les valeurs hors-set mais on prévient/erreur strictement si explicitement incorrecte
            if statut not in allowed_statuts and len(statut) > 50:
                raise ValueError("statut_marital invalide ou trop long")

        niveau_edu = value.get("niveau_education")
        if niveau_edu is not None:
            if not isinstance(niveau_edu, int) or not (0 <= niveau_edu <= 10):
                raise ValueError("niveau_education doit être un entier raisonnable (0–10)")

        domaine = value.get("domaine_etude")
        if domaine is not None:
            if not isinstance(domaine, str) or not domaine.strip():
                raise ValueError("domaine_etude doit être une chaîne non vide")
            if len(domaine) > 100:
                raise ValueError("domaine_etude trop long")

        # --- EMPLOI / POSTE ---
        departement = value.get("departement")
        poste = value.get("poste")
        if departement is not None and (not isinstance(departement, str) or len(departement) > 100):
            raise ValueError("departement invalide ou trop long")
        if poste is not None and (not isinstance(poste, str) or len(poste) > 100):
            raise ValueError("poste invalide ou trop long")

        niveau_hier = value.get("niveau_hierarchique_poste")
        if niveau_hier is not None:
            if not isinstance(niveau_hier, int) or niveau_hier < 0 or niveau_hier > 20:
                raise ValueError("niveau_hierarchique_poste doit être un entier raisonnable (0–20)")

        # --- SALAIRE ---
        revenu = value.get("revenu_mensuel")
        if revenu is not None and revenu <= 0:
            raise ValueError("revenu_mensuel doit être positif")

        augmentation = value.get("augementation_salaire_precedente")
        if augmentation is not None and augmentation < 0:
            raise ValueError("augmentation salaire négative interdite")

        salaire_par_annee_exp = value.get("salaire_par_annee_exp")
        if salaire_par_annee_exp is not None:
            if salaire_par_annee_exp <= 0:
                raise ValueError("salaire_par_annee_exp doit être positif")
            # si revenu mensuel fourni, on peut vérifier la cohérence approximative
            if revenu is not None and abs(salaire_par_annee_exp - (revenu * 12)) > (revenu * 12) * 0.5:
                # tolérance large (50%) pour éviter faux positifs
                raise ValueError("incohérence importante entre revenu_mensuel et salaire_par_annee_exp")

        # --- DEPLACEMENT ---
        freq = value.get("frequence_deplacement")
        if freq not in [0, 1, 2]:
            raise ValueError("frequence_deplacement doit être 0, 1 ou 2")

        distance = value.get("distance_domicile_travail")
        if distance is not None and distance < 0:
            raise ValueError("distance_domicile_travail invalide")

        distance_x = value.get("distance_x_deplacement")
        if distance_x is not None and distance_x < 0:
            raise ValueError("distance_x_deplacement invalide")

        impact_trajet = value.get("impact_trajet_sur_satisfaction")
        if impact_trajet is not None and not (0 <= impact_trajet <= 5):
            raise ValueError("impact_trajet_sur_satisfaction doit être entre 0 et 5")

        # --- HEURES SUP ---
        hs = value.get("heure_supplementaires")
        if hs not in [0, 1]:
            raise ValueError("heure_supplementaires doit être 0 ou 1")

        # --- EVALUATIONS ---
        note_actuelle = value.get("note_evaluation_actuelle")
        note_precedente = value.get("note_evaluation_precedente")

        if note_actuelle is not None and not (1 <= note_actuelle <= 5):
            raise ValueError("note_evaluation_actuelle hors plage (1–5)")

        if note_precedente is not None and not (1 <= note_precedente <= 5):
            raise ValueError("note_evaluation_precedente hors plage (1–5)")

        evolution_note = value.get("evolution_note")
        if evolution_note is not None:
            # si on a les deux notes, on vérifie la cohérence
            if note_actuelle is not None and note_precedente is not None:
                if evolution_note != (note_actuelle - note_precedente):
                    raise ValueError("evolution_note incohérente avec note_actuelle et note_precedente")
            else:
                # sinon, on vérifie qu'il est dans un intervalle raisonnable
                if not (-4 <= evolution_note <= 4):
                    raise ValueError("evolution_note hors plage raisonnable (-4–4)")

        # --- SATISFACTION ---
        for field in [
            "satisfaction_employee_nature_travail",
            "satisfaction_employee_environnement",
            "satisfaction_employee_equilibre_pro_perso",
            "satisfaction_employee_equipe",
            "satisfaction_moyenne",
            "score_satisfaction_global",
        ]:
            val = value.get(field)
            if val is not None and not (0 <= val <= 5):
                raise ValueError(f"{field} doit être entre 0 et 5")

        delta_eq = value.get("delta_satisfaction_equipe")
        if delta_eq is not None and not (-5 <= delta_eq <= 5):
            raise ValueError("delta_satisfaction_equipe hors plage (-5–5)")

        # --- VOLATILITE ---
        volatilite = value.get("taux_volatilite")
        if volatilite is not None and not (0 <= volatilite <= 1):
            raise ValueError("taux_volatilite doit être entre 0 et 1")

        # --- RATIOS ---
        ratio_fidelite = value.get("ratio_fidelite_entreprise")
        if ratio_fidelite is not None and not (0 <= ratio_fidelite <= 1):
            raise ValueError("ratio_fidelite_entreprise doit être entre 0 et 1")

        ratio_poste = value.get("ratio_poste_vs_anciennete")
        if ratio_poste is not None and not (0 <= ratio_poste <= 1):
            raise ValueError("ratio_poste_vs_anciennete doit être entre 0 et 1")

        anciennete_x_sat = value.get("anciennete_x_satisfaction")
        if anciennete_x_sat is not None and anciennete_x_sat < 0:
            raise ValueError("anciennete_x_satisfaction ne peut pas être négatif")

        # --- EXPERIENCES / FORMATIONS ---
        nb_exp_prev = value.get("nombre_experiences_precedentes")
        if nb_exp_prev is not None and (not isinstance(nb_exp_prev, int) or nb_exp_prev < 0):
            raise ValueError("nombre_experiences_precedentes doit être un entier >= 0")

        nb_form = value.get("nb_formations_suivies")
        if nb_form is not None and (not isinstance(nb_form, int) or nb_form < 0):
            raise ValueError("nb_formations_suivies doit être un entier >= 0")

        form_par_an = value.get("formations_par_annee")
        if form_par_an is not None and form_par_an < 0:
            raise ValueError("formations_par_annee doit être >= 0")
        if nb_form is not None and form_par_an is not None:
            # protection simple : formations par an ne devrait pas dépasser nb total de formations
            if form_par_an > nb_form:
                raise ValueError("formations_par_annee ne peut pas dépasser nb_formations_suivies")

        participe_pee = value.get("nombre_participation_pee")
        if participe_pee is not None and (not isinstance(participe_pee, int) or participe_pee < 0):
            raise ValueError("nombre_participation_pee doit être un entier >= 0")

        # --- STAGNATION ---
        for field in ["stagnation_poste", "stagnation_profonde"]:
            v = value.get(field)
            if v not in [0, 1]:
                raise ValueError(f"{field} doit être 0 ou 1")

        return value





class ModelOutput(Base):
    __tablename__ = "model_outputs"

    id = Column(Integer, primary_key=True)

    input_id = Column(
        Integer,
        ForeignKey("model_inputs.id", ondelete="CASCADE"),
        nullable=False
    )

    # Prédiction du modèle (churn / non churn)
    prediction = Column(Integer, nullable=False)

    # Probabilité associée
    probability = Column(Float)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    input = relationship("ModelInput", back_populates="outputs")

    # -------- RÈGLES ORM SQL (CONTRAINTES DB) --------
    __table_args__ = (
        CheckConstraint(
            "prediction IN (0, 1)",
            name="check_prediction_binary"
        ),
        CheckConstraint(
            "probability IS NULL OR (probability >= 0 AND probability <= 1)",
            name="check_probability_range"
        ),
    )
